import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DATABASE_PATH = 'database.db'
ASSETS_PATH = 'assets'
POOL_FILE = 'cards_pool.json'

# ==================== ECONOMIA ====================
DAILY_VALOR = 25000          # R$ por /daily
DAILY_COOLDOWN_HORAS = 24
OBTER_COOLDOWN_SEGUNDOS = 5
MAX_TITULARES = 7            # 1 GOL + 6 jogadores de linha (varia por formação)
TAXA_PAY = 0.10               # 10% de taxa no /pay

# ==================== SORTEIO GRATUITO (/obter) ====================
# pesos de raridade do sorteio grátis — bem baixo pra OURO/LENDÁRIO, já que
# não custa nada (diferente dos pacotes pagos do /buypack)
OBTER_PESOS_RARIDADE = {'COMUM': 70, 'BRONZE': 24, 'PRATA': 5, 'OURO': 0.8, 'LENDÁRIO': 0.2}

# ==================== PACOTES (/buypack) ====================
# cada pacote tem um preço e o peso de chance de cada raridade (quanto maior o
# peso, mais chance — pesos são relativos entre si, não precisam somar 100)
PACOTES = {
    'Bronze Pack': {
        'preco': 300000,
        'pesos': {'COMUM': 68, 'BRONZE': 27, 'PRATA': 4.5, 'OURO': 0.5, 'LENDÁRIO': 0},
    },
    'Silver Pack': {
        'preco': 600000,
        'pesos': {'COMUM': 45, 'BRONZE': 38, 'PRATA': 14, 'OURO': 2.7, 'LENDÁRIO': 0.3},
    },
    'Gold Pack': {
        'preco': 1250000,
        'pesos': {'COMUM': 25, 'BRONZE': 35, 'PRATA': 28, 'OURO': 10.5, 'LENDÁRIO': 1.5},
    },
    'Diamond': {
        'preco': 5000000,
        'pesos': {'COMUM': 10, 'BRONZE': 20, 'PRATA': 35, 'OURO': 25, 'LENDÁRIO': 10},
    },
}

# ==================== TESTMATCH ====================
# partida de treino contra um time da CPU — vitória paga a recompensa cheia,
# empate paga metade, derrota não paga nada
TESTMATCH_NIVEIS = {
    'Easy':   {'overall': 80, 'recompensa': 5000},
    'Medium': {'overall': 85, 'recompensa': 10000},
    'Hard':   {'overall': 90, 'recompensa': 20000},
}

# ==================== FORMAÇÕES ====================
# quantidade de DEF / MEI / ATA em cada formação (GOL é sempre 1, fixo)
FORMACOES = {
    '2-2-2': {'DEF': 2, 'MEI': 2, 'ATA': 2},
    '3-1-2': {'DEF': 3, 'MEI': 1, 'ATA': 2},
    '1-2-3': {'DEF': 1, 'MEI': 2, 'ATA': 3},
}
FORMACAO_PADRAO = '2-2-2'

# ==================== RARIDADES ====================
# (nome, emoji, estrelas, overall_min, overall_max)
RARIDADES = [
    ("COMUM",     "🟢", 1, 0,  59),
    ("BRONZE",    "🥉", 2, 60, 69),
    ("PRATA",     "⚪", 3, 70, 79),
    ("OURO",      "🟡", 4, 80, 89),
    ("LENDÁRIO",  "💎", 5, 90, 100),
]

# Raridades que disparam o anúncio no canal de puxadas raras (as duas mais altas
# que existem hoje — não há um nível "ÉPICA" separado, se você criar um, é só
# adicionar o nome dele aqui)
RARIDADES_ANUNCIADAS = ["OURO", "LENDÁRIO"]

# ==================== CANAIS ====================
# canal onde é anunciado quando alguém tira uma carta OURO/LENDÁRIO no /obter
CANAL_RARAS = 1546334975865921657

# únicos canais onde os comandos do bot podem ser usados (vazio = sem restrição)
CANAIS_PERMITIDOS = [
    1546553588602507386,
    1546553621821530214,
    1546553643443159070,
]

# ==================== CAMPEONATOS (/campeonato) ====================
# campeonato solo contra times da CPU — cada tipo define a faixa de overall
# dos adversários e quantos times de CPU entram no chaveamento (+ você).
# 'formato': 'copa' = grupos + mata-mata | 'final_unica' = um jogo só (Recopa)
TIPOS_CAMPEONATO = {
    # --- nacionais/continentais grandes ---
    'Copinha':              {'premio': 250000,   'overall_min': 60, 'overall_max': 75, 'adversarios': 7, 'formato': 'copa'},
    'Copa do Brasil':       {'premio': 500000,   'overall_min': 75, 'overall_max': 85, 'adversarios': 7, 'formato': 'copa'},
    'Libertadores':         {'premio': 1000000,  'overall_min': 82, 'overall_max': 92, 'adversarios': 7, 'formato': 'copa'},
    'Sul-Americana':        {'premio': 700000,   'overall_min': 78, 'overall_max': 88, 'adversarios': 7, 'formato': 'copa'},
    'Argentino':            {'premio': 450000,   'overall_min': 74, 'overall_max': 86, 'adversarios': 7, 'formato': 'copa'},

    # --- estaduais ---
    'Paulistão':            {'premio': 150000,   'overall_min': 65, 'overall_max': 78, 'adversarios': 7, 'formato': 'copa'},
    'Carioca':              {'premio': 150000,   'overall_min': 65, 'overall_max': 78, 'adversarios': 7, 'formato': 'copa'},
    'Mineirão':             {'premio': 150000,   'overall_min': 65, 'overall_max': 78, 'adversarios': 7, 'formato': 'copa'},
    'Gaúcho':               {'premio': 120000,   'overall_min': 62, 'overall_max': 75, 'adversarios': 7, 'formato': 'copa'},
    'Baiano':               {'premio': 100000,   'overall_min': 60, 'overall_max': 74, 'adversarios': 7, 'formato': 'copa'},

    # --- jogo único (campeão da Libertadores x campeão da Sul-Americana) ---
    'Recopa Sul-Americana': {'premio': 1200000,  'overall_min': 88, 'overall_max': 92, 'adversarios': 1, 'formato': 'final_unica'},
}

# cooldown pra jogar de novo o MESMO campeonato/Brasileirão (tipos diferentes
# não têm cooldown entre si — só repetir o mesmo é limitado)
CAMPEONATO_COOLDOWN_MINUTOS = 10

# ==================== BRASILEIRÃO (/brasileirao) ====================
# liga persistente: você começa na Série D e sobe/desce entre divisões,
# igual futebol de verdade:
#   - Série D: formato de copa (grupos + mata-mata) — só o campeão sobe
#   - Séries C/B/A: pontos corridos — você + 8 times de CPU jogam todos
#     contra todos (cada confronto uma vez só = 32 jogos cada), sobe quem fica na zona de
#     acesso, desce quem fica na zona de rebaixamento
DIVISOES_BRASILEIRAO = {
    'D': {
        'formato': 'copa',
        'overall_min': 55, 'overall_max': 65,
        'adversarios': 7,  # você + 7 CPU = 8 times -> 2 grupos de 4 + mata-mata
        'premio': 10000,
        'sobe': 'C', 'desce': None,
    },
    'C': {
        'formato': 'liga',
        'overall_min': 65, 'overall_max': 75,
        'adversarios': 32,  # você + 32 CPU = 33 times, cada confronto 1x = 32 jogos
        'premio': 30000,
        'sobe': 'B', 'desce': 'D',
        'zona_acesso': 4, 'zona_rebaixamento': 4,
    },
    'B': {
        'formato': 'liga',
        'overall_min': 75, 'overall_max': 85,
        'adversarios': 32,
        'premio': 75000,
        'sobe': 'A', 'desce': 'C',
        'zona_acesso': 4, 'zona_rebaixamento': 4,
    },
    'A': {
        'formato': 'liga',
        'overall_min': 85, 'overall_max': 95,
        'adversarios': 32,
        'premio': 200000,
        'sobe': None, 'desce': 'B',
        'zona_acesso': 0, 'zona_rebaixamento': 4,
    },
}
DIVISAO_PADRAO = 'D'
