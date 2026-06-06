"""pages/entrada.py"""
import datetime, streamlit as st
from utils.database import (buscar_produto_por_ean, buscar_produtos_por_nome,
    criar_produto, registrar_movimentacao, criar_documento,
    upload_pdf, listar_categorias, listar_movimentacoes, buscar_produto_por_id)
from utils.auth import sessao
from utils.ui import badge
from utils.fmt import datahora_br, qtd_br
from utils.unidades import SIGLAS, OPCOES, sigla_para_opcao, opcao_para_sigla

TIPOS=["Nota Fiscal","FL","Entrada Interna","Ajuste Manual"]

def _u(label,val="UN",key=None):
    idx=SIGLAS.index(val) if val in SIGLAS else 0
    kw={"key":key} if key else {}
    return opcao_para_sigla(st.selectbox(label,OPCOES,index=idx,**kw))

def tela_entrada():
    st.markdown('<div class="pg">',unsafe_allow_html=True)
    st.markdown('<div class="pg-title">📥 Entrada de Produtos</div><div class="pg-sub">Registre entradas por EAN, nome ou cadastro avulso</div>',unsafe_allow_html=True)
    t1,t2=st.tabs(["Nova Entrada","Histórico"])
    with t1: _form()
    with t2: _hist()
    st.markdown("</div>",unsafe_allow_html=True)

def _form():
    u=sessao(); cats=listar_categorias(); cm={c["nome"]:c["id"] for c in cats}
    prod=st.session_state.get("ps")
    st.markdown('<div class="card"><div class="card-h">🔍 Identificar Produto</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns([3,1,1])
    with c1: termo=st.text_input("EAN ou nome",placeholder="Bipe ou digite",key="eb")
    with c2:
        st.markdown("<div style='height:27px'></div>",unsafe_allow_html=True)
        be=st.button("Buscar EAN",use_container_width=True)
    with c3:
        st.markdown("<div style='height:27px'></div>",unsafe_allow_html=True)
        bn=st.button("Buscar Nome",use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)
    if be and termo.strip():
        p=buscar_produto_por_ean(termo.strip())
        if p: st.session_state["ps"]=p; st.session_state.pop("en",None); prod=p; st.success(f"✅ {p['nome']} — {p['codigo_interno']}")
        else: st.warning("EAN não encontrado. Cadastre abaixo."); st.session_state.pop("ps",None); st.session_state["en"]=termo.strip()
    if bn and termo.strip():
        res=buscar_produtos_por_nome(termo.strip())
        if res:
            opts={f"{r['nome']} ({r['codigo_interno']})":r for r in res}
            sel=st.selectbox("Selecione",list(opts.keys()),key="snr")
            if st.button("Usar este →"): st.session_state["ps"]=opts[sel]; st.session_state.pop("en",None); st.rerun()
        else: st.warning("Não encontrado."); st.session_state.pop("ps",None)
    if prod:
        est=float(prod.get("quantidade_total_secundaria",0)); fat=float(prod.get("fator_conversao",1))
        up=prod.get("unidade_primaria","UN"); us=prod.get("unidade_secundaria","UN")
        up_lbl=sigla_para_opcao(up); us_lbl=sigla_para_opcao(us)
        st.markdown(f'<div style="background:var(--ok-bg);border:1px solid rgba(22,163,74,.25);border-radius:8px;padding:.8rem 1.1rem;margin:.5rem 0;font-size:.84rem;">✅ <strong>{prod["nome"]}</strong> &nbsp;<span class="mono" style="color:var(--t3);">{prod["codigo_interno"]}</span>{" &nbsp;|&nbsp; EAN: "+prod["ean"] if prod.get("ean") else ""} &nbsp;|&nbsp; Estoque: <strong style="color:var(--ok);">{qtd_br(est)} {us_lbl}</strong> <span style="color:var(--t3);font-size:.75rem;">(= {qtd_br(est/fat if fat else 0)} {up_lbl})</span></div>',unsafe_allow_html=True)
        st.markdown('<div class="card"><div class="card-h">📥 Registrar Nova Entrada</div>',unsafe_allow_html=True)
        with st.form("fer"):
            c1,c2=st.columns(2)
            with c1:
                te=st.selectbox("Tipo de entrada *",TIPOS)
                qtd=st.number_input("Quantidade *",min_value=0.001,value=1.0,step=1.0)
                ui=_u("Unidade informada",val=up,key="ui_ent")
            with c2: nfn=st.text_input("Número NF",placeholder="Opcional"); forn=st.text_input("Fornecedor",placeholder="Opcional"); obs=st.text_area("Obs",height=60)
            qc=qtd*fat; ui_lbl=sigla_para_opcao(ui)
            st.markdown(f'<div style="background:var(--bg2);border:1px solid var(--bdr);border-radius:7px;padding:.65rem .9rem;margin:.4rem 0;font-size:.8rem;">📦 <strong>{qtd_br(qtd)} {ui_lbl}</strong> <span style="color:var(--t3);">=</span> <strong style="color:var(--red);">{qtd_br(qc)} {us_lbl}</strong> adicionados</div>',unsafe_allow_html=True)
            pdf=None
            if te=="Nota Fiscal": pdf=st.file_uploader("📎 PDF da Nota Fiscal (necessário para gerar alerta de envio)",type=["pdf","png","jpg"])
            else: pdf=st.file_uploader("📎 Anexar comprovante (opcional)",type=["pdf","png","jpg"])
            if st.form_submit_button("✅ Confirmar Entrada",type="primary",use_container_width=True):
                did=None
                if pdf:
                    ts=datetime.datetime.now().strftime("%Y%m%d%H%M%S"); nm=f"{ts}_{pdf.name}"
                    url=upload_pdf(pdf.read(),nm) if pdf.type=="application/pdf" else None
                    doc=criar_documento({"nome_arquivo":pdf.name,"caminho_arquivo":url,"status_envio":"pendente" if te=="Nota Fiscal" else "nao_requer"})
                    did=doc["id"]
                gerar=te=="Nota Fiscal" and pdf is not None
                registrar_movimentacao({"produto_id":prod["id"],"tipo":"entrada","tipo_entrada":te,"status":"concluido","quantidade_informada":qtd,"unidade_informada":ui,"quantidade_convertida":qc,"envio_financeiro":not gerar,"fornecedor":forn.strip() or None,"numero_nf":nfn.strip() or None,"observacao":obs.strip() or None,"documento_id":did,"usuario_executor":u["id"],"data_movimentacao":datetime.datetime.utcnow().isoformat()})
                st.success(f"✅ +{qtd_br(qc)} {us_lbl} de **{prod['nome']}** por **{u.get('nick','')}**.")
                if gerar: st.info("📎 NF registrada — acesse Notas Fiscais para enviar.")
                elif te=="Nota Fiscal" and not pdf: st.warning("⚠️ Entrada NF sem PDF — nenhuma pendência criada.")
                p_novo=buscar_produto_por_id(prod["id"])
                if p_novo: st.session_state["ps"]=p_novo
                st.rerun()
        ca,cb=st.columns(2)
        with ca:
            if st.button("🔄 Buscar outro produto",use_container_width=True):
                for k in ["ps","en"]: st.session_state.pop(k,None); st.rerun()
        with cb:
            if st.button("➕ Nova entrada deste produto",use_container_width=True):
                p_novo=buscar_produto_por_id(prod["id"])
                if p_novo: st.session_state["ps"]=p_novo; st.rerun()
        st.markdown("</div>",unsafe_allow_html=True); return
    with st.expander("➕ Cadastrar Produto"):
        with st.form("fnp"):
            st.markdown('<div style="font-size:.78rem;color:var(--t3);margin-bottom:.5rem;">O EAN é opcional mas facilita buscas futuras.</div>',unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1: nm=st.text_input("Nome *"); cat=st.selectbox("Categoria",list(cm.keys())); up_n=_u("Un. primária",val="CX",key="upn"); us_n=_u("Un. secundária",val="UN",key="usn")
            with c2: fat_n=st.number_input("Fator (1 prim=? sec)",value=1.0,min_value=0.001,step=1.0); em_n=st.number_input("Estoque mínimo (prim)",value=0.0,min_value=0.0); ean_n=st.text_input("EAN / Código de barras (opcional)",value=st.session_state.get("en",""),placeholder="Deixe em branco se não tiver")
            desc_n=st.text_area("Descrição (opcional)",height=60)
            if st.form_submit_button("Cadastrar Produto →",type="primary",use_container_width=True):
                if not nm.strip(): st.error("Nome obrigatório.")
                else:
                    d={"nome":nm.strip(),"categoria_id":cm.get(cat),"unidade_primaria":up_n,"unidade_secundaria":us_n,"fator_conversao":fat_n,"estoque_minimo_primario":em_n,"descricao":desc_n.strip() or None}
                    if ean_n.strip(): d["ean"]=ean_n.strip()
                    novo=criar_produto(d); st.session_state["ps"]=novo; st.session_state.pop("en",None)
                    st.success(f"✅ {novo['nome']} — {novo['codigo_interno']}"); st.rerun()

def _hist():
    movs=listar_movimentacoes(tipo="entrada",limite=100)
    if not movs: st.info("Nenhuma entrada."); return
    st.markdown('<div class="card"><div class="card-h">Histórico de Entradas</div>',unsafe_allow_html=True)
    rows=""
    for m in movs:
        prod=(m.get("produto") or {}).get("nome","—"); cod=(m.get("produto") or {}).get("codigo_interno","—")
        eu=(m.get("exe") or {}).get("nick","—"); tp=badge(m.get("tipo_entrada","—"),"concluido")
        un_lbl=sigla_para_opcao(m.get("unidade_informada","UN"))
        rows+=f'<tr><td style="color:var(--t3);font-size:.73rem;">{datahora_br(m["criado_em"])}</td><td><strong>{prod}</strong></td><td class="mono">{cod}</td><td style="font-weight:600;">{qtd_br(m["quantidade_informada"])} {un_lbl}</td><td>{tp}</td><td style="color:var(--t3);">{m.get("numero_nf") or "—"}</td><td style="color:var(--t3);">{eu}</td></tr>'
    st.markdown(f'<table class="tbl"><thead><tr><th>Data</th><th>Produto</th><th>Código</th><th>Qtd</th><th>Tipo</th><th>NF</th><th>Executor</th></tr></thead><tbody>{rows}</tbody></table>',unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
