"""utils/unidades.py — Mapa de unidades com sigla e nome por extenso"""

UNIDADES_MAP = {
    "UN":  "UN (Unidade)",
    "CX":  "CX (Caixa)",
    "KG":  "KG (Quilograma)",
    "LT":  "LT (Litro)",
    "MT":  "MT (Metro)",
    "PC":  "PC (Peça)",
    "RL":  "RL (Rolo)",
    "FR":  "FR (Frasco)",
    "GL":  "GL (Galão)",
    "DZ":  "DZ (Dúzia)",
    "CT":  "CT (Centena)",
    "SC":  "SC (Saco)",
    "FD":  "FD (Fardo)",
    "BL":  "BL (Bloco)",
    "PT":  "PT (Pacote)",
    "PR":  "PR (Par)",
    "TB":  "TB (Tubo)",
    "CJ":  "CJ (Conjunto)",
    "FL":  "FL (Folha)",
    "GR":  "GR (Grama)",
}

# Lista apenas das siglas (para selectbox)
SIGLAS = list(UNIDADES_MAP.keys())

# Lista com "SIGLA (Nome)" (para exibição no selectbox)
OPCOES = list(UNIDADES_MAP.values())

def sigla_para_opcao(sigla: str) -> str:
    """Retorna 'UN (Unidade)' dado 'UN'"""
    return UNIDADES_MAP.get(sigla, sigla)

def opcao_para_sigla(opcao: str) -> str:
    """Retorna 'UN' dado 'UN (Unidade)'"""
    if opcao in UNIDADES_MAP:
        return opcao
    for sig, nome in UNIDADES_MAP.items():
        if nome == opcao:
            return sig
    return opcao.split(" ")[0]  # fallback

def selectbox_unidade(label: str, valor_atual: str = "UN", key: str = None) -> str:
    """Renderiza selectbox com sigla + nome. Retorna a SIGLA selecionada."""
    import streamlit as st
    idx = SIGLAS.index(valor_atual) if valor_atual in SIGLAS else 0
    kwargs = {"key": key} if key else {}
    sel = st.selectbox(label, OPCOES, index=idx, **kwargs)
    return opcao_para_sigla(sel)
