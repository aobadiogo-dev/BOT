# VOF Guru

Bot de Discord de gacha/elenco de jogadores de futebol, no estilo do DreamTeam,
com arquitetura em Cogs.

## Estrutura

```
vof_guru/
├── main.py            # inicializa o bot e carrega os Cogs
├── config.py           # constantes (economia, cooldowns, raridades, campeonatos, Brasileirão)
├── database.py         # camada de acesso ao SQLite (usuários)
├── cards.py             # pool global de jogadores (definições e sorteio)
├── campo.py              # geração da imagem do campo tático (Pillow)
├── campeonato.py          # simulação de campeonatos solo e temporada de liga (Brasileirão)
├── simulacao.py            # motor de simulação de partidas (placar por overall)
├── sorte.py                  # evento temporário que multiplica chance de OURO/LENDÁRIO
├── utils.py                    # helpers de embed compartilhados
├── cogs/
│   ├── economia.py      # /saldo /daily /pay
│   ├── mercado.py       # /obter /comprar /buypack /cesta_basica
│   ├── elenco.py         # /elenco /carta /vercarta /promover /reserva
│   ├── time_cog.py       # /time /formacao
│   ├── jogo.py            # /jogar /testmatch
│   ├── campeonato.py       # /campeonato /brasileirao
│   ├── admin.py            # /addplayer /deletarplayer /listaplayers /limpar_duplicatas /setar /sorte
│   └── ajuda.py              # /help
├── requirements.txt
├── runtime.txt
├── discloud.json
└── .env.example
```

## Instalação local

```bash
pip install -r requirements.txt
cp .env.example .env
# edite o .env e cole o token do seu bot
python main.py
```

⚠️ **Segurança:** o `.env` real (com o token) nunca deve ser commitado nem
compartilhado em zip/arquivo. Se um token já vazou (apareceu num arquivo
compartilhado, print, repositório público etc.), resete-o imediatamente no
Portal de Desenvolvedores do Discord (Bot → Reset Token) antes de colocar o
bot em produção — um token vazado permite que qualquer pessoa controle o bot.

## Comandos

| Comando | Descrição |
|---|---|
| `/help` | Lista todos os comandos por categoria |
| `/saldo` | Veja seu saldo na liga |
| `/daily` | Resgata a recompensa diária (cooldown configurável) |
| `/pay <user> <amount>` | Manda dinheiro pra outro usuário (com taxa) |
| `/obter` | Sorteia um jogador do banco (cooldown curto) — vem com botões "Escalar como Titular" e "Vender" |
| `/buypack <pack>` | Compra um pacote (Bronze/Silver/Gold/Diamond) com chances melhores de raridades altas |
| `/cesta_basica` | Recebe 7 jogadores aleatórios 85+ OVR das posições DEF, MEI, GOL/GK e ATA (uma vez por usuário) |
| `/comprar` | Abre o mercado de transferências |
| `/elenco [usuario]` | Mostra o campo tático com titulares e reservas |
| `/carta <nome>` | Mostra a carta de um jogador do seu elenco |
| `/vercarta <usuario> <nome>` | Visualiza a carta de um jogador de outro usuário |
| `/promover <nome>` | Promove um jogador do banco para titular (respeita a formação) |
| `/reserva <nome>` | Move um titular de volta para a reserva |
| `/formacao [formacao]` | Vê ou troca a formação: 2-2-2, 3-1-2 ou 1-2-3 |
| `/time [nome] [sigla]` | Vê ou define o nome/sigla do seu time |
| `/jogar <oponente>` | Simula uma partida contra outro jogador |
| `/testmatch <difficulty>` | Partida de treino contra a CPU — paga recompensa se vencer/empatar |
| `/campeonato <tipo>` | Disputa um campeonato inteiro contra times da CPU (Copa do Brasil, Libertadores, Sul-Americana, estaduais, Recopa, etc.) |
| `/brasileirao` | Disputa a temporada na sua série atual (Série D é copa; C/B/A são pontos corridos) — sobe/desce pela posição |
| `/addplayer` (ADM) | Adiciona um jogador ao banco global |
| `/deletarplayer` (ADM) | Remove um jogador do banco global |
| `/listaplayers` (ADM) | Lista todos os jogadores do banco global |
| `/limpar_duplicatas` (ADM) | Remove cópias duplicadas dos elencos de todos os usuários |
| `/setar` (ADM) | Adiciona um jogador diretamente ao elenco de um membro |
| `/sorte [multiplicador] [duracao_minutos]` (ADM) | Ativa/desativa um evento que multiplica a chance de OURO/LENDÁRIO |

## Canais

- Os comandos só funcionam nos canais listados em `config.CANAIS_PERMITIDOS` (deixe a lista vazia `[]` pra liberar em qualquer canal).
- Cartas **OURO** e **LENDÁRIO** tiradas no `/obter` ou `/buypack` são anunciadas automaticamente no canal `config.CANAL_RARAS`.

## Notas de design

- Cada jogador **contratado** (via `/obter`, `/comprar`, `/buypack` ou `/cesta_basica`) vira uma
  **instância** própria (`instancia_id`) guardada no elenco do usuário —
  isso permite ter cartas repetidas e o `/limpar_duplicatas` remover as extras.
- `/obter` sorteia do banco global gratuitamente (respeitando o cooldown);
  `/buypack` cobra um preço e melhora as chances de raridades altas;
  `/comprar` deixa escolher exatamente quem contratar, pagando o valor de
  mercado definido no `/addplayer`.
- Raridade é calculada automaticamente pelo overall do jogador
  (COMUM/BRONZE/PRATA/OURO/LENDÁRIO) — ajuste as faixas em `config.py`.
- Cada formação define quantos DEF/MEI/ATA cabem como titular (GOL é sempre 1)
  — ajuste em `config.FORMACOES`. Trocar de formação rebaixa automaticamente
  quem não couber mais.
- `/campeonato` e `/brasileirao` simulam adversários da CPU com overall
  sorteado dentro da faixa configurada por tipo/divisão em `config.py`.
