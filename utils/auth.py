"""utils/auth.py — Autenticação por nick + senha"""
import bcrypt, streamlit as st
from utils.database import buscar_por_nick, contar_usuarios

def hash_senha(s: str) -> str:
    return bcrypt.hashpw(s.encode(), bcrypt.gensalt()).decode()

def verificar_senha(s: str, h: str) -> bool:
    try: return bcrypt.checkpw(s.encode(), h.encode())
    except: return False

def fazer_login(nick: str, senha: str):
    u = buscar_por_nick(nick)
    if not u or not u.get("ativo"): return None
    if not verificar_senha(senha, u["senha_hash"]): return None
    return u

def sessao():
    return st.session_state.get("usuario")

def primeiro_acesso() -> bool:
    return contar_usuarios() == 0

def is_admin() -> bool:
    u = sessao(); return u is not None and u["perfil"] == "admin"

def is_almoxarife() -> bool:
    u = sessao(); return u is not None and u["perfil"] in ("admin", "almoxarife")

def is_usuario_simples() -> bool:
    u = sessao(); return u is not None and u["perfil"] == "usuario"

def pode(acao: str) -> bool:
    u = sessao()
    if not u: return False
    p = u["perfil"]
    m = {
        # admin e almoxarife veem dashboard
        "dashboard":      ["admin","almoxarife"],
        "entrada":        ["admin","almoxarife"],
        # Saída manual e aprovada: apenas admin e almoxarife
        "saida_manual":   ["admin","almoxarife"],
        "saida_aprovada": ["admin","almoxarife"],
        "estoque":        ["admin","almoxarife"],
        "notas":          ["admin","almoxarife"],
        "usuarios":       ["admin"],
        "configuracoes":  ["admin"],
        # Solicitar: todos os perfis
        "solicitar":      ["admin","almoxarife","usuario"],
        # Solicitações COMPLETA (nova + aprovar + histórico): admin
        # Almoxarife só vê aprovações e histórico (tratado na página)
        "solicitacoes":   ["admin","almoxarife","usuario"],
        # Aprovar: apenas admin
        "aprovar":        ["admin"],
    }
    return p in m.get(acao, [])
