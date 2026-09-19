import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cards as cards_mod
from config import FORMACOES, FORMACAO_PADRAO

CAMPO_BASE = 'assets/campo_base.png'
CARD_W, CARD_H = 102, 138

FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_LABEL_SIZE = 16

RARIDADE_COR = {
    'COMUM':    (70, 200, 120),
    'BRONZE':   (190, 120, 60),
    'PRATA':    (200, 200, 210),
    'OURO':     (235, 185, 45),
    'LENDÁRIO': (110, 140, 255),
}

# Linhas (y) de cada categoria no campo (648x1050 — reduzido pra economizar RAM)
Y_ATA, Y_MEI, Y_DEF, Y_GOL = 228, 492, 732, 936

# Posições X pra cada quantidade de slots numa linha (até 3 por linha)
X_POR_QTD = {
    1: [324],
    2: [180, 468],
    3: [114, 324, 534],
}

# Compatibilidade com esquemas de posição antigos (das versões anteriores do bot)
MAPA_POSICAO_ANTIGA = {
    'GOL': 'GOL',
    'DEF': 'DEF', 'ZAG': 'DEF', 'LE': 'DEF', 'LD': 'DEF',
    'MEI': 'MEI', 'VOL': 'MEI', 'MC': 'MEI',
    'ATA': 'ATA', 'ST': 'ATA', 'PE': 'ATA', 'PD': 'ATA', 'CA': 'ATA',
}


def posicao_normalizada(posicao):
    return MAPA_POSICAO_ANTIGA.get(posicao, 'MEI')


def montar_slots(formacao):
    """Retorna a lista [(categoria, x, y), ...] pra uma formação (ex: '2-2-2')."""
    config_formacao = FORMACOES.get(formacao, FORMACOES[FORMACAO_PADRAO])
    slots = [('GOL', X_POR_QTD[1][0], Y_GOL)]
    for categoria, y in (('DEF', Y_DEF), ('MEI', Y_MEI), ('ATA', Y_ATA)):
        qtd = config_formacao[categoria]
        for x in X_POR_QTD[qtd]:
            slots.append((categoria, x, y))
    return slots


def total_slots(formacao):
    return len(montar_slots(formacao))


def _fonte(tamanho):
    try:
        return ImageFont.truetype(FONT_PATH, tamanho)
    except Exception:
        return ImageFont.load_default()


def _desenhar_pill(draw, cx, cy, texto, font):
    w, h = 42, 24
    box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    draw.rounded_rectangle(box, radius=6, fill=(10, 10, 14, 230), outline=(255, 255, 255, 60), width=1)
    bbox = draw.textbbox((0, 0), texto, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2, cy - th / 2 - bbox[1]), texto, font=font, fill=(255, 255, 255, 255))


def _colar_carta(campo, cx, cy, img_bytes, cor_glow):
    carta_original = Image.open(io.BytesIO(img_bytes)).convert('RGBA')
    carta_original.thumbnail((CARD_W, CARD_H), Image.LANCZOS)

    # sempre centraliza a carta numa caixa de tamanho FIXO (CARD_W x CARD_H),
    # não importa a proporção da imagem original — é isso que fazia o rótulo
    # e o brilho ficarem "tortos" (mais pra cima ou mais pra baixo) antes
    carta_fixa = Image.new('RGBA', (CARD_W, CARD_H), (0, 0, 0, 0))
    offset = ((CARD_W - carta_original.width) // 2, (CARD_H - carta_original.height) // 2)
    carta_fixa.paste(carta_original, offset, carta_original)

    glow = Image.new('RGBA', (CARD_W + 36, CARD_H + 36), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.rounded_rectangle([18, 18, CARD_W + 17, CARD_H + 17], radius=11, fill=cor_glow + (150,))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    campo.paste(glow, (cx - CARD_W // 2 - 18, cy - CARD_H // 2 - 18), glow)
    campo.paste(carta_fixa, (cx - CARD_W // 2, cy - CARD_H // 2), carta_fixa)


def gerar_imagem_campo(titulares, formacao=FORMACAO_PADRAO):
    """
    titulares: lista de instâncias do elenco (dicts com player_id, posicao, nome, overall).
    formacao: '2-2-2', '3-1-2' ou '1-2-3' — define quantos slots de DEF/MEI/ATA existem.
    Retorna os bytes do PNG final.
    """
    campo = Image.open(CAMPO_BASE).convert('RGBA')
    draw = ImageDraw.Draw(campo, 'RGBA')
    font_label = _fonte(FONT_LABEL_SIZE)

    por_categoria = {}
    for j in titulares:
        cat = posicao_normalizada(j['posicao'])
        por_categoria.setdefault(cat, []).append(j)

    usados = {cat: 0 for cat in por_categoria}

    for categoria, x, y in montar_slots(formacao):
        fila = por_categoria.get(categoria, [])
        indice = usados.get(categoria, 0)
        if indice >= len(fila):
            _desenhar_pill(draw, x, y, categoria, font_label)
            continue
        usados[categoria] = indice + 1
        jogador = fila[indice]

        img_bytes = cards_mod.carregar_imagem(jogador['player_id'])
        if not img_bytes:
            _desenhar_pill(draw, x, y, categoria, font_label)
            continue

        raridade = cards_mod.calcular_raridade(jogador['overall'])
        cor_glow = RARIDADE_COR.get(raridade['nome'], (255, 255, 255))
        _colar_carta(campo, x, y, img_bytes, cor_glow)
        _desenhar_pill(draw, x, y + CARD_H // 2 + 16, categoria, font_label)

    buffer = io.BytesIO()
    campo.convert('RGB').save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.getvalue()
