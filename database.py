import json
import aiosqlite
from config import DATABASE_PATH, FORMACAO_PADRAO, DIVISAO_PADRAO


class Database:
    """Camada de acesso ao banco de usuários da VOF Guru.

    Cada linha de `usuarios` guarda:
      - saldo: dinheiro do usuário (R$)
      - banco: lista JSON de instâncias de jogadores (reservas / não titulares)
      - titulares: lista JSON de instancia_id que estão escalados como titular
      - time_nome / time_sigla: identidade do time do usuário
    Cada "instância" de jogador é um dict:
      {"instancia_id": "<uuid4 hex>", "player_id": "<id no pool>",
       "nome": ..., "posicao": ..., "overall": ...}
    """

    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f'''
                CREATE TABLE IF NOT EXISTS usuarios (
                    user_id     TEXT PRIMARY KEY,
                    username    TEXT,
                    saldo       INTEGER DEFAULT 0,
                    last_daily  TEXT,
                    last_obter  TEXT,
                    cesta_basica_usada INTEGER DEFAULT 0,
                    banco       TEXT DEFAULT '[]',
                    titulares   TEXT DEFAULT '[]',
                    time_nome   TEXT,
                    time_sigla  TEXT,
                    formacao    TEXT DEFAULT '{FORMACAO_PADRAO}',
                    divisao_brasileirao TEXT DEFAULT '{DIVISAO_PADRAO}',
                    campeonatos_cd TEXT DEFAULT '{{}}',
                    recopa_pendente TEXT
                )
            ''')
            await db.commit()

            # Migração: se a tabela já existia de uma versão anterior (com
            # colunas diferentes, ex. 'coins'/'jogadores'/'formacao'), garante
            # que todas as colunas novas existem sem apagar dados antigos.
            cursor = await db.execute('PRAGMA table_info(usuarios)')
            colunas_existentes = {row[1] for row in await cursor.fetchall()}

            colunas_necessarias = {
                'saldo': "INTEGER DEFAULT 0",
                'last_daily': "TEXT",
                'last_obter': "TEXT",
                'cesta_basica_usada': "INTEGER DEFAULT 0",
                'banco': "TEXT DEFAULT '[]'",
                'titulares': "TEXT DEFAULT '[]'",
                'time_nome': "TEXT",
                'time_sigla': "TEXT",
                'formacao': f"TEXT DEFAULT '{FORMACAO_PADRAO}'",
                'divisao_brasileirao': f"TEXT DEFAULT '{DIVISAO_PADRAO}'",
                'campeonatos_cd': "TEXT DEFAULT '{}'",
                'recopa_pendente': "TEXT",
            }
            for coluna, definicao in colunas_necessarias.items():
                if coluna not in colunas_existentes:
                    await db.execute(f'ALTER TABLE usuarios ADD COLUMN {coluna} {definicao}')
                    print(f"✅ Coluna '{coluna}' adicionada à tabela usuarios (migração)")

            await db.commit()
            await db.commit()
            print("✅ Banco de dados inicializado")

    # ---------------- usuários ----------------

    async def get_user(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM usuarios WHERE user_id = ?', (str(user_id),)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def create_user(self, user_id, username):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT OR IGNORE INTO usuarios
                   (user_id, username, saldo, banco, titulares)
                   VALUES (?, ?, 0, '[]', '[]')''',
                (str(user_id), username)
            )
            await db.commit()

    async def get_or_create_user(self, user_id, username):
        user = await self.get_user(user_id)
        if not user:
            await self.create_user(user_id, username)
            user = await self.get_user(user_id)
        return user

    async def update_user(self, user_id, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            updates, values = [], []
            for key, value in kwargs.items():
                updates.append(f"{key} = ?")
                if key in ('banco', 'titulares'):
                    values.append(json.dumps(value, ensure_ascii=False))
                else:
                    values.append(value)
            values.append(str(user_id))
            query = f"UPDATE usuarios SET {', '.join(updates)} WHERE user_id = ?"
            await db.execute(query, values)
            await db.commit()

    async def add_saldo(self, user_id, amount):
        user = await self.get_user(user_id)
        if user:
            await self.update_user(user_id, saldo=user['saldo'] + amount)

    async def get_ranking(self, limit=10):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT user_id, username, saldo FROM usuarios ORDER BY saldo DESC LIMIT ?',
                (limit,)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_all_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('SELECT * FROM usuarios')
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    # ---------------- helpers de elenco (JSON) ----------------

    @staticmethod
    def get_banco(user_row):
        return json.loads(user_row['banco']) if user_row['banco'] else []

    @staticmethod
    def get_titulares_ids(user_row):
        return json.loads(user_row['titulares']) if user_row['titulares'] else []

    @staticmethod
    def get_campeonatos_cd(user_row):
        return json.loads(user_row['campeonatos_cd']) if user_row.get('campeonatos_cd') else {}

    async def set_campeonato_jogado_agora(self, user_id, tipo):
        from datetime import datetime
        user = await self.get_user(user_id)
        cds = self.get_campeonatos_cd(user)
        cds[tipo] = datetime.now().isoformat()
        await self.update_user(user_id, campeonatos_cd=json.dumps(cds, ensure_ascii=False))
