import io
import discord
import cards as cards_mod


def montar_embed_carta(jogador, player_id, titulo="🎴 Carta do Jogador", autor_nome=None,
                        chance=None, elenco_total=None, cor=discord.Color.blue()):
    """Monta o embed + arquivo de imagem para exibir a carta de um jogador do pool."""
    raridade = cards_mod.calcular_raridade(jogador['overall'])
    estrelas = cards_mod.estrelas_texto(raridade['estrelas'])

    desc = ""
    if autor_nome:
        desc += f"**{autor_nome}**\n\n"
    desc += (
        f"**Jogador:** {jogador['nome']}\n"
        f"{raridade['emoji']} {raridade['nome']} · {estrelas}\n"
        "\u2015" * 12 + "\n\n"
        f"📍 **Posição**\n{jogador['posicao']}\n\n"
        f"📊 **Overall**\n{jogador['overall']} OVR\n\n"
        f"🏳️ **Clube**\n{jogador.get('clube', '—')}\n\n"
        f"💰 **Valor de Mercado**\nR$ {jogador['valor_mercado']:,.2f}\n\n"
        f"💵 **Valor de Venda**\nR$ {jogador['valor_venda']:,.2f}\n"
    )
    if elenco_total is not None:
        desc += f"\n📁 **Elenco Total**\n{elenco_total} jogador(es)\n"
    if chance is not None:
        desc += (
            f"\n✨ **Detalhes do Sorteio**\n"
            f"Raridade: {raridade['emoji']} {raridade['nome']} · Chance obtida: ~{chance}%\n"
        )

    embed = discord.Embed(title=titulo, description=desc, color=cor)

    img_bytes = cards_mod.carregar_imagem(player_id)
    file = None
    if img_bytes:
        file = discord.File(io.BytesIO(img_bytes), filename="carta.png")
        embed.set_image(url="attachment://carta.png")

    return embed, file


def formatar_dinheiro(valor):
    return f"R$ {valor:,.2f}"
