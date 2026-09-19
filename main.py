import sys
import asyncio
import traceback
import discord
from discord import app_commands
from discord.ext import commands
from config import DISCORD_TOKEN, CANAIS_PERMITIDOS
from database import Database

if not DISCORD_TOKEN:
    print("❌ DISCORD_TOKEN não encontrado no .env!")
    sys.exit(1)

intents = discord.Intents.default()
intents.guilds = True
intents.members = False           # não precisamos de cache de membros — economiza RAM
intents.message_content = False   # só usamos slash commands, não lemos mensagens


class VOFCommandTree(app_commands.CommandTree):
    """CommandTree com duas travas globais:
    1. Anti-duplicidade: se a mesma interação chegar mais de uma vez (ex: duas
       instâncias do bot rodando com o mesmo token), só a primeira é processada.
    2. Canal restrito: comandos só funcionam nos canais listados em
       config.CANAIS_PERMITIDOS (lista vazia = sem restrição, libera geral)."""

    def __init__(self, client):
        super().__init__(client)
        self._interacoes_processadas = set()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.id in self._interacoes_processadas:
            print(f"⚠️ Interação duplicada ignorada (id={interaction.id}). "
                  f"Verifique se não há mais de uma instância do bot rodando com o mesmo token.")
            return False
        self._interacoes_processadas.add(interaction.id)
        if len(self._interacoes_processadas) > 2000:
            self._interacoes_processadas = set(list(self._interacoes_processadas)[-1000:])

        if CANAIS_PERMITIDOS and interaction.channel_id not in CANAIS_PERMITIDOS:
            mencoes = " ".join(f"<#{cid}>" for cid in CANAIS_PERMITIDOS)
            await interaction.response.send_message(
                f"❌ Esse comando só pode ser usado em: {mencoes}", ephemeral=True
            )
            return False
        return True


bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    tree_cls=VOFCommandTree,
    chunk_guilds_at_startup=False,                       # não baixa a lista de membros do servidor
    member_cache_flags=discord.MemberCacheFlags.none(),  # não guarda cache de membros em RAM
    max_messages=None,                                   # não guarda cache de mensagens (não usamos)
)
bot.db = Database()

COGS = [
    'cogs.economia',
    'cogs.mercado',
    'cogs.elenco',
    'cogs.time_cog',
    'cogs.jogo',
    'cogs.admin',
    'cogs.ajuda',
    'cogs.campeonato',
]


@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    print(f'📊 Conectado em {len(bot.guilds)} servidor(es)')
    await bot.db.init_db()
    try:
        synced = await bot.tree.sync()
        print(f"✅ Comandos sincronizados: {len(synced)}")
        for cmd in synced:
            print(f"   - /{cmd.name}")
    except Exception as e:
        print(f"⚠️ Erro na sincronização: {e}")


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handler global: garante que todo erro aparece no console (com traceback
    completo) e que o usuário recebe uma resposta em vez do bot 'não responder'."""
    print(f"❌ Erro no comando /{interaction.command.name if interaction.command else '?'}:")
    traceback.print_exception(type(error), error, error.__traceback__)

    msg = "❌ Deu erro ao executar esse comando. Já ficou registrado no log pra investigar."
    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        pass  # se nem isso der, não tem mais o que fazer


async def main():
    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                print(f"✅ Cog carregado: {cog}")
            except Exception as e:
                print(f"❌ Erro ao carregar {cog}: {e}")
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    print("🚀 Iniciando VOF GURU...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Bot encerrado.")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)
