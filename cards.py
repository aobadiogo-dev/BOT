import os
import json
import random
import requests
from config import ASSETS_PATH, POOL_FILE, RARIDADES

os.makedirs(ASSETS_PATH, exist_ok=True)


# ==================== CARREGAR / SALVAR POOL ====================

def carregar_pool():
    if os.path.exists(POOL_FILE):
        with open(POOL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def salvar_pool(pool):
    with open(POOL_FILE, 'w', encoding='utf-8') as f:
        json.dump(pool, f, indent=2, ensure_ascii=False)


# ==================== IMAGEM ====================

def baixar_imagem(url, nome_arquivo):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            caminho = os.path.join(ASSETS_PATH, nome_arquivo)
            with open(caminho, 'wb') as f:
                f.write(response.content)
            return caminho
        print(f"❌ Erro ao baixar {nome_arquivo}: status {response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Erro ao baixar {nome_arquivo}: {e}")
        return None


def carregar_imagem(player_id):
    jogador = get_jogador_por_id(player_id)
    if not jogador:
        return None
    caminho = os.path.join(ASSETS_PATH, jogador['arquivo'])
    if os.path.exists(caminho):
        with open(caminho, 'rb') as f:
            return f.read()
    return None


# ==================== RARIDADE ====================

def calcular_raridade(overall):
    for nome, emoji, estrelas, minimo, maximo in RARIDADES:
        if minimo <= overall <= maximo:
            return {"nome": nome, "emoji": emoji, "estrelas": estrelas}
    return {"nome": RARIDADES[-1][0], "emoji": RARIDADES[-1][1], "estrelas": RARIDADES[-1][2]}


def estrelas_texto(qtd, total=5):
    return "★" * qtd + "☆" * (total - qtd)


# ==================== CRUD DO POOL ====================

def adicionar_jogador(nome, posicao, overall, clube, preco, url_imagem):
    pool = carregar_pool()
    for j in pool.values():
        if j['nome'].lower() == nome.lower():
            return False, f"Já existe um jogador chamado **{nome}** no banco.", None

    novo_id = str(max([int(k) for k in pool.keys()], default=0) + 1)
    nome_arquivo = f"jogador_{novo_id}_{nome.lower().replace(' ', '_')}.png"

    if not baixar_imagem(url_imagem, nome_arquivo):
        return False, "Não consegui baixar a imagem informada.", None

    pool[novo_id] = {
        'nome': nome,
        'posicao': posicao,
        'overall': overall,
        'clube': clube,
        'valor_mercado': preco,
        'valor_venda': int(preco * 0.6),
        'arquivo': nome_arquivo,
    }
    salvar_pool(pool)
    return True, f"Jogador **{nome}** (#{novo_id}) adicionado ao banco!", novo_id


def deletar_jogador(player_id):
    pool = carregar_pool()
    if player_id not in pool:
        return False, "Jogador não encontrado no banco."
    nome = pool[player_id]['nome']
    del pool[player_id]
    salvar_pool(pool)
    return True, f"Jogador **{nome}** (#{player_id}) removido do banco."


def listar_pool():
    return carregar_pool()


def listar_jogadores_cesta_basica(overall_minimo=85):
    """Retorna jogadores elegíveis para o pacote gratuito /cesta_basica."""
    posicoes_validas = {'DEF', 'MEI', 'GOL', 'GK', 'ATA'}
    return {
        player_id: jogador
        for player_id, jogador in carregar_pool().items()
        if str(jogador.get('posicao', '')).strip().upper() in posicoes_validas
        and jogador.get('overall', 0) >= overall_minimo
    }


def get_jogador_por_id(player_id):
    return carregar_pool().get(str(player_id))


def get_jogador_por_nome(nome):
    for pid, info in carregar_pool().items():
        if info['nome'].lower() == nome.lower():
            return pid, info
    return None, None


def _sortear_uniforme(pool):
    """Sorteio simples, sem pesar raridade — usado como fallback quando os
    pesos configurados não têm nenhuma raridade presente no pool."""
    player_id = random.choice(list(pool.keys()))
    jogador = pool[player_id]
    raridade = calcular_raridade(jogador['overall'])
    mesma_raridade = [
        j for j in pool.values()
        if calcular_raridade(j['overall'])['nome'] == raridade['nome']
    ]
    chance = round(len(mesma_raridade) / len(pool) * 100, 2)
    return player_id, jogador, chance


def get_jogador_aleatorio():
    """Sorteia um jogador do pool pro /obter, respeitando OBTER_PESOS_RARIDADE
    (sorteio grátis tem chance bem menor de OURO/LENDÁRIO que os pacotes pagos).
    Se tiver um evento de /sorte ativo, os pesos de OURO/LENDÁRIO são multiplicados.
    Retorna (id, dados, chance%)."""
    from config import OBTER_PESOS_RARIDADE
    import sorte as sorte_mod
    pesos = sorte_mod.aplicar_multiplicador(OBTER_PESOS_RARIDADE)
    return sortear_por_pesos(pesos)


def sortear_por_pesos(pesos_raridade):
    """Sorteia um jogador do pool respeitando pesos por raridade (usado por
    /buypack — pacotes mais caros têm pesos maiores pras raridades altas).
    Retorna (id, dados, chance%) ou (None, None, 0) se o pool estiver vazio."""
    pool = carregar_pool()
    if not pool:
        return None, None, 0

    por_raridade = {}
    for pid, info in pool.items():
        nome_raridade = calcular_raridade(info['overall'])['nome']
        por_raridade.setdefault(nome_raridade, []).append(pid)

    # só considera raridades que existem no pool E têm peso > 0
    tiers_validos = [r for r in pesos_raridade if r in por_raridade and pesos_raridade[r] > 0]
    if not tiers_validos:
        # fallback: se nenhuma raridade do peso existe no pool, sorteia geral
        return _sortear_uniforme(pool)

    pesos = [pesos_raridade[r] for r in tiers_validos]
    raridade_sorteada = random.choices(tiers_validos, weights=pesos, k=1)[0]
    player_id = random.choice(por_raridade[raridade_sorteada])

    chance = round(pesos_raridade[raridade_sorteada] / sum(pesos) * 100, 2)
    return player_id, pool[player_id], chance
