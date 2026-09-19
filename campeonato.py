import random
import simulacao

# Nomes de CPU separados por "peso" de divisão, pra ficar mais realista —
# clubes tradicionalmente grandes aparecem na Série A, times menores na
# Série C/D, igual futebol de verdade.
NOMES_ELITE = [  # Série A — clubes grandes/tradicionais
    "Flamengo", "Palmeiras", "Corinthians", "São Paulo", "Santos",
    "Grêmio", "Internacional", "Atlético-MG", "Cruzeiro", "Fluminense",
    "Botafogo", "Vasco da Gama", "Bahia", "Fortaleza", "Athletico-PR",
    "Bragantino", "Cuiabá", "Atlético-GO", "Vitória", "Criciúma",
]

NOMES_MEIO = [  # Série B — times tradicionais que oscilam entre A/B
    "Coritiba", "Sport Recife", "Ceará", "Goiás", "Náutico",
    "América-MG", "Guarani", "Juventude", "Avaí", "Chapecoense",
    "Paraná Clube", "Vila Nova", "CRB", "Operário-PR", "Ponte Preta",
    "Novorizontino", "Ituano", "Mirassol", "Sampaio Corrêa", "Botafogo-PB",
]

NOMES_MENOR = [  # Série C — clubes menores, típicos dessa divisão
    "CSA", "Londrina", "ABC", "Confiança", "Remo",
    "Paysandu", "Ferroviária", "São Bernardo", "Volta Redonda", "Tombense",
    "Caxias", "São José-RS", "Brusque", "Anápolis", "Floresta",
    "Aparecidense", "Maringá", "Figueirense", "Ypiranga-RS", "Altos-PI",
]

NOMES_REGIONAL = [  # Série D — times pequenos/regionais
    "Nova Iguaçu", "Cianorte", "Retrô", "Central", "Sergipe",
    "Trem-AP", "Manaus FC", "Real Ariquemes", "Barra-SC", "Camboriú",
    "ASA", "Treze-PB", "Juazeirense", "Porto Velho", "Rio Branco-AC",
    "Náutico-RR", "Genus", "Costa Rica-MS", "Rondoniense", "Independente-AP",
]

# fallback genérico, usado quando não é chamado com um pool específico de divisão
NOMES_CPU = NOMES_ELITE + NOMES_MEIO + NOMES_MENOR + NOMES_REGIONAL


def jogar_partida(a, b):
    return simulacao.jogar_partida(a['media'], b['media'])


def gerar_adversarios_cpu(quantidade, overall_min, overall_max, pool=None):
    fonte = pool if pool else NOMES_CPU
    nomes = random.sample(fonte, k=min(quantidade, len(fonte)))
    extra = 2
    while len(nomes) < quantidade:  # se precisar de mais do que os nomes disponíveis, usa "II", "III"...
        base = fonte[(len(nomes)) % len(fonte)]
        nomes.append(f"{base} {['II','III','IV','V'][extra % 4]}")
        extra += 1
    return [
        {'user_id': f"cpu_{i}", 'nome_time': nome, 'media': random.randint(overall_min, overall_max)}
        for i, nome in enumerate(nomes)
    ]


def _montar_grupos(participantes, tamanho_grupo=4):
    embaralhados = participantes[:]
    random.shuffle(embaralhados)
    num_grupos = max(1, -(-len(embaralhados) // tamanho_grupo))  # divisão arredondando pra cima
    grupos = [[] for _ in range(num_grupos)]
    for i, p in enumerate(embaralhados):
        grupos[i % num_grupos].append(p)
    return grupos


def _rodar_grupo(grupo):
    pontos = {p['user_id']: 0 for p in grupo}
    saldo_gols = {p['user_id']: 0 for p in grupo}
    linhas = []

    for i in range(len(grupo)):
        for j in range(i + 1, len(grupo)):
            a, b = grupo[i], grupo[j]
            gols_a, gols_b = jogar_partida(a, b)
            saldo_gols[a['user_id']] += gols_a - gols_b
            saldo_gols[b['user_id']] += gols_b - gols_a
            if gols_a > gols_b:
                pontos[a['user_id']] += 3
            elif gols_b > gols_a:
                pontos[b['user_id']] += 3
            else:
                pontos[a['user_id']] += 1
                pontos[b['user_id']] += 1
            linhas.append(f"{a['nome_time']} {gols_a} x {gols_b} {b['nome_time']}")

    classificacao = sorted(
        grupo,
        key=lambda p: (pontos[p['user_id']], saldo_gols[p['user_id']]),
        reverse=True
    )
    tabela = "\n".join(
        f"{i + 1}. {p['nome_time']} — {pontos[p['user_id']]} pts (saldo {saldo_gols[p['user_id']]:+d})"
        for i, p in enumerate(classificacao)
    )
    return classificacao, "\n".join(linhas), tabela


def _mata_mata(classificados):
    fase_atual = classificados[:]
    random.shuffle(fase_atual)
    log = []
    numero_fase = 1

    while len(fase_atual) > 1:
        proxima_fase = []
        nome_fase = "**FINAL**" if len(fase_atual) == 2 else f"**Fase {numero_fase}**"
        log.append(f"{nome_fase} ({len(fase_atual)} times)")

        if len(fase_atual) % 2 == 1:
            bye = fase_atual.pop()
            proxima_fase.append(bye)
            log.append(f"— {bye['nome_time']} avança de bye")

        for i in range(0, len(fase_atual), 2):
            a, b = fase_atual[i], fase_atual[i + 1]
            gols_a, gols_b = jogar_partida(a, b)
            if gols_a == gols_b:
                chance_a = 0.5 + (a['media'] - b['media']) / 200
                vencedor = a if random.random() < chance_a else b
                log.append(f"— {a['nome_time']} {gols_a} x {gols_b} {b['nome_time']} (pênaltis: {vencedor['nome_time']})")
            else:
                vencedor = a if gols_a > gols_b else b
                log.append(f"— {a['nome_time']} {gols_a} x {gols_b} {b['nome_time']}")
            proxima_fase.append(vencedor)

        fase_atual = proxima_fase
        numero_fase += 1

    return fase_atual[0], "\n".join(log)


def rodar_campeonato_solo(nome_time_usuario, media_usuario, config_tipo, pool=None):
    """Monta você + N times de CPU (config_tipo['adversarios']) e roda o
    campeonato. Se 'formato' for 'final_unica' (ex: Recopa Sul-Americana),
    joga só uma partida direto contra o único adversário, sem grupos/mata-mata.
    'pool' (opcional) restringe os nomes de CPU a uma lista específica (ex:
    times menores pra Série D). Retorna o relatório completo, incluindo se
    você foi campeão."""
    seu_time = {'user_id': 'voce', 'nome_time': nome_time_usuario, 'media': media_usuario}
    adversarios = gerar_adversarios_cpu(
        config_tipo['adversarios'], config_tipo['overall_min'], config_tipo['overall_max'], pool=pool
    )

    relatorio = {'grupos': [], 'mata_mata': "", 'campeao': None, 'voce_venceu': False}

    if config_tipo.get('formato') == 'final_unica':
        adversario = adversarios[0]
        gols_a, gols_b = jogar_partida(seu_time, adversario)
        if gols_a == gols_b:
            chance_a = 0.5 + (seu_time['media'] - adversario['media']) / 200
            campeao = seu_time if random.random() < chance_a else adversario
            relatorio['mata_mata'] = (
                f"**FINAL ÚNICA**\n— {seu_time['nome_time']} {gols_a} x {gols_b} {adversario['nome_time']} "
                f"(pênaltis: {campeao['nome_time']})"
            )
        else:
            campeao = seu_time if gols_a > gols_b else adversario
            relatorio['mata_mata'] = f"**FINAL ÚNICA**\n— {seu_time['nome_time']} {gols_a} x {gols_b} {adversario['nome_time']}"
        relatorio['campeao'] = campeao
        relatorio['voce_venceu'] = campeao['user_id'] == 'voce'
        return relatorio

    participantes = [seu_time] + adversarios

    if len(participantes) <= 3:
        classificados = participantes
    else:
        grupos = _montar_grupos(participantes)
        classificados = []
        for idx, grupo in enumerate(grupos, start=1):
            if len(grupo) < 2:
                classificados.extend(grupo)
                continue
            classificacao, resultados, tabela = _rodar_grupo(grupo)
            relatorio['grupos'].append({'nome': f"Grupo {idx}", 'resultados': resultados, 'tabela': tabela})
            classificados.extend(classificacao[:2])

    campeao, log_mata_mata = _mata_mata(classificados)
    relatorio['mata_mata'] = log_mata_mata
    relatorio['campeao'] = campeao
    relatorio['voce_venceu'] = campeao['user_id'] == 'voce'
    return relatorio


def rodar_temporada_liga(nome_time_usuario, media_usuario, config_divisao, pool=None):
    """Pontos corridos 'de verdade': você + N times de CPU jogam todos contra
    todos, cada confronto só uma vez (sem jogo de ida e volta) — com N=32 CPU
    dá exatamente 32 jogos por time na temporada. 'pool' (opcional) restringe
    os nomes de CPU pra uma lista específica da divisão. Retorna a tabela
    final completa.
    """
    seu_time = {'user_id': 'voce', 'nome_time': nome_time_usuario, 'media': media_usuario}
    adversarios = gerar_adversarios_cpu(
        config_divisao['adversarios'], config_divisao['overall_min'], config_divisao['overall_max'], pool=pool
    )
    times = [seu_time] + adversarios

    stats = {
        t['user_id']: {'pontos': 0, 'v': 0, 'e': 0, 'd': 0, 'gp': 0, 'gc': 0, 'jogos': 0}
        for t in times
    }

    for i in range(len(times)):
        for j in range(i + 1, len(times)):
            a, b = times[i], times[j]
            gols_a, gols_b = jogar_partida(a, b)
            sa, sb = stats[a['user_id']], stats[b['user_id']]
            sa['jogos'] += 1
            sb['jogos'] += 1
            sa['gp'] += gols_a
            sa['gc'] += gols_b
            sb['gp'] += gols_b
            sb['gc'] += gols_a
            if gols_a > gols_b:
                sa['v'] += 1
                sa['pontos'] += 3
                sb['d'] += 1
            elif gols_b > gols_a:
                sb['v'] += 1
                sb['pontos'] += 3
                sa['d'] += 1
            else:
                sa['e'] += 1
                sb['e'] += 1
                sa['pontos'] += 1
                sb['pontos'] += 1

    ranking = sorted(
        times,
        key=lambda t: (stats[t['user_id']]['pontos'], stats[t['user_id']]['gp'] - stats[t['user_id']]['gc'], stats[t['user_id']]['gp']),
        reverse=True
    )
    posicao_voce = next(i for i, t in enumerate(ranking, start=1) if t['user_id'] == 'voce')

    return {
        'ranking': ranking,
        'stats': stats,
        'posicao_voce': posicao_voce,
        'total_times': len(times),
        'jogos_por_time': stats[times[0]['user_id']]['jogos'],
    }
