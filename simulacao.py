import random


def prob_resultado(media_a, media_b):
    """Retorna (p_vitoria_a, p_empate, p_vitoria_b), somando 1.
    Quanto maior a diferença de overall, mais decisivo o resultado tende a
    ser — um time 90+ deve esmagar um time 60-65 na grande maioria das vezes,
    upset ainda é possível mas deve ser raro."""
    diff = media_a - media_b
    p_empate = max(0.08, min(0.28, 0.26 - abs(diff) * 0.006))
    decisivo = 1 - p_empate
    p_a_no_decisivo = 1 / (1 + 10 ** (-diff / 9))
    p_vitoria_a = decisivo * p_a_no_decisivo
    p_vitoria_b = decisivo * (1 - p_a_no_decisivo)
    return p_vitoria_a, p_empate, p_vitoria_b


def _gols_do_vencedor(diferenca_absoluta):
    if diferenca_absoluta < 5:
        return random.choices([1, 2, 3], weights=[45, 40, 15])[0]
    elif diferenca_absoluta < 15:
        return random.choices([1, 2, 3, 4], weights=[25, 40, 25, 10])[0]
    else:
        return random.choices([2, 3, 4, 5], weights=[30, 35, 25, 10])[0]


def jogar_partida(media_a, media_b):
    """Simula uma partida com base na diferença de overall entre os dois
    lados. Retorna (gols_a, gols_b)."""
    p_a, p_empate, p_b = prob_resultado(media_a, media_b)
    resultado = random.choices(['a', 'empate', 'b'], weights=[p_a, p_empate, p_b])[0]
    diferenca_absoluta = abs(media_a - media_b)

    if resultado == 'empate':
        gols = random.choices([0, 1, 2], weights=[35, 45, 20])[0]
        return gols, gols
    elif resultado == 'a':
        gols_a = _gols_do_vencedor(diferenca_absoluta)
        gols_b = random.randint(0, gols_a - 1)
        return gols_a, gols_b
    else:
        gols_b = _gols_do_vencedor(diferenca_absoluta)
        gols_a = random.randint(0, gols_b - 1)
        return gols_a, gols_b
