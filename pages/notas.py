"""pages/notas.py"""
import urllib.parse, streamlit as st
from utils.database import listar_notas_pendentes,listar_notas_enviadas,atualizar_movimentacao,get_config
from utils.auth import sessao
from utils.ui import badge,kpi_html
from utils.fmt import datahora_br

def tela_notas():
    st.markdown('<div class="pg">',unsafe_allow_html=True)
    st.markdown('<div class="pg-title">📎 Notas Fiscais</div><div class="pg-sub">Gerencie e envie ao financeiro</div>',unsafe_allow_html=True)
    p=listar_notas_pendentes(); e=listar_notas_enviadas()
    st.markdown(f'<div class="kpis" style="grid-template-columns:repeat(3,1fr);margin-bottom:1.2rem;">{kpi_html("Total NF",len(p)+len(e),"","var(--t2)")}{kpi_html("Pendentes",len(p),"Aguardando envio","var(--warn)")}{kpi_html("Enviadas",len(e),"Processadas","var(--ok)")}</div>',unsafe_allow_html=True)
    t1,t2=st.tabs([f"Pendentes ({len(p)})",f"Enviadas ({len(e)})"])
    with t1: _lista(p,True)
    with t2: _lista(e,False)
    st.markdown("</div>",unsafe_allow_html=True)

def _lista(movs,pendente):
    u=sessao()
    ed=get_config("email_financeiro","financeiro@empresa.com.br")
    es=get_config("email_assunto","[NF] Nota Fiscal - SFC Almoxarifado")
    eb=get_config("email_corpo","Prezados,\n\nSegue nota fiscal.\n\nAtenciosamente,")
    if not movs:
        st.markdown(f'<p style="color:var(--t3);font-size:.82rem;padding:1rem 0;">{"Nenhuma nota pendente." if pendente else "Nenhuma nota enviada."}</p>',unsafe_allow_html=True); return
    for m in movs:
        prod=m.get("produto") or {}; doc=m.get("doc") or {}
        eu=(m.get("exe") or {}).get("nick","—"); nfn=m.get("numero_nf") or "—"; forn=m.get("fornecedor") or "—"
        bx=badge("Pendente","pendente") if pendente else badge("Enviado","enviado")
        pdf_url=doc.get("caminho_arquivo")
        st.markdown('<div class="card">',unsafe_allow_html=True)
        c1,c2,c3=st.columns([4,3,3])
        with c1:
            st.markdown(f"**NF {nfn}** — {forn} &nbsp;{bx}",unsafe_allow_html=True)
            st.markdown(f"<span style='font-size:.77rem;color:var(--t3);'>{prod.get('nome','—')}</span>",unsafe_allow_html=True)
            st.caption(f"Registrada em {datahora_br(m.get('criado_em'))} por {eu}")
        with c2:
            if pdf_url: st.link_button("📄 Visualizar PDF",pdf_url)
            else: st.markdown("<span style='font-size:.75rem;color:var(--t4);'>Sem arquivo</span>",unsafe_allow_html=True)
        with c3:
            if pendente:
                nome_u=u.get("nome") or u.get("nick","")
                corpo=f"{eb}\n\nNF: {nfn}\nFornecedor: {forn}\nProduto: {prod.get('nome','')}"
                if pdf_url: corpo+=f"\n\nLink do documento: {pdf_url}"
                corpo+=f"\n\nAtenciosamente,\n{nome_u}\nSFC Almoxarifado"
                mailto=f"mailto:{ed}?subject={urllib.parse.quote(es)}&body={urllib.parse.quote(corpo)}"
                st.link_button("📧 Abrir no Outlook",mailto)
                if pdf_url: st.markdown('<div style="font-size:.72rem;color:var(--info);margin:.3rem 0;">ℹ️ Baixe o PDF pelo link acima e anexe ao e-mail antes de enviar.</div>',unsafe_allow_html=True)
                if st.button("✅ Enviei — Remover da lista",key=f"env_{m['id']}",use_container_width=True):
                    st.session_state[f"conf_nf_{m['id']}"]=True; st.rerun()
            if st.session_state.get(f"conf_nf_{m['id']}"):
                st.markdown('<div style="background:var(--warn-bg);border:1px solid rgba(217,119,6,.3);border-radius:7px;padding:.7rem .9rem;font-size:.8rem;margin:.4rem 0;">⚠️ Confirma que o e-mail foi enviado e deseja remover esta nota?</div>',unsafe_allow_html=True)
                cs,cn=st.columns(2)
                with cs:
                    if st.button("✅ Sim, remover",key=f"sim_nf_{m['id']}",type="primary",use_container_width=True):
                        atualizar_movimentacao(m["id"],{"envio_financeiro":True})
                        del st.session_state[f"conf_nf_{m['id']}"]; st.success("Nota removida!"); st.rerun()
                with cn:
                    if st.button("↩ Voltar",key=f"nao_nf_{m['id']}",use_container_width=True):
                        del st.session_state[f"conf_nf_{m['id']}"]; st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
