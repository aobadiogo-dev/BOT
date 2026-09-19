import json
import os
from datetime import datetime, timedelta

ARQUIVO_SORTE = 'sorte.json'
RARIDADES_COM_BOOST = ['OURO', 'LENDÁRIO']


def _carregar():
    if os.path.exists(ARQUIVO_SORTE):
        with open(ARQUIVO_SORTE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def _salvar(estado):
    with open(ARQUIVO_SORTE, 'w', encoding='utf-8') as f:
        json.dump(estado, f)


def ativar(multiplicador, minutos):
    expira_em = (datetime.now() + timedelta(minutes=minutos)).isoformat()
    _salvar({'multiplicador': multiplicador, 'expira_em': expira_em})


def desativar():
    if os.path.exists(ARQUIVO_SORTE):
        os.remove(ARQUIVO_SORTE)


def status():
    """Retorna {'multiplicador': X, 'restante': timedelta} se tiver um evento
    ativo (e ainda dentro do prazo), ou None se não tiver nenhum rolando."""
    estado = _carregar()
    if not estado:
        return None
    expira_em = datetime.fromisoformat(estado['expira_em'])
    if datetime.now() >= expira_em:
        desativar()
        return None
    return {'multiplicador': estado['multiplicador'], 'restante': expira_em - datetime.now()}


def multiplicador_ativo():
    s = status()
    return s['multiplicador'] if s else 1


def aplicar_multiplicador(pesos_raridade):
    """Recebe um dict de pesos (ex: config.OBTER_PESOS_RARIDADE ou o pacote de
    /buypack) e devolve uma cópia com OURO/LENDÁRIO multiplicados pelo evento
    de sorte ativo (se não tiver nenhum ativo, devolve igualzinho)."""
    mult = multiplicador_ativo()
    if mult == 1:
        return pesos_raridade
    novo = dict(pesos_raridade)
    for raridade in RARIDADES_COM_BOOST:
        if raridade in novo:
            novo[raridade] = novo[raridade] * mult
    return novo
