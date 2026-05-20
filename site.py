import streamlit as st

from auth import inicializar_sessao, tela_login, logout
from database import buscar_historico
from analyzer import analisar_edital
from pdf_generator import gerar_pdf
from styles import aplicar_estilo
from opportunities import tela_oportunidades
from saved_opportunities import tela_oportunidades_salvas
from alerts import tela_alertas


st.set_page_config(
    page_title="CredMed IA",
    page_icon="🏥",
    layout="wide"
)

aplicar_estilo()
inicializar_sessao()

if st.session_state.user is None:
    tela_login()

user_email = st.session_state.user
historico = buscar_historico(user_email)

with st.sidebar:
    st.markdown("## 🏥 CredMed IA")
    st.success(f"Logado como:\n\n{user_email}")

    pagina = st.radio(
        "Navegação",
        [
            "Painel",
            "Radar de Oportunidades",
            "Base Inteligente",
            "Meus Alertas"
        ]
    )

    if st.button("Sair"):
        logout()

    st.markdown("---")
    st.markdown("## 📂 Histórico")

    if historico:
        for item in historico:
            with st.expander(f"📄 {item['nome_arquivo'][:28]}"):
                st.caption(item["criado_em"])

                if st.button(f"Abrir análise {item['id']}", key=f"abrir_{item['id']}"):
                    st.session_state.resultado_antigo = item["resultado"]
                    st.rerun()
    else:
        st.info("Nenhuma análise encontrada.")


if pagina == "Painel":

    st.markdown("""
    <div class="hero">
        <h1>🏥 CredMed IA</h1>
        <h3>
        Plataforma SaaS para análise inteligente de credenciamentos,
        licitações públicas e oportunidades na saúde.
        </h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Análises feitas</div>
            <div class="metric-value">{len(historico)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Plano atual</div>
            <div class="metric-value">FREE</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Radar PNCP</div>
            <div class="metric-value">ON</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Status</div>
            <div class="metric-value">BETA</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h2>📄 Nova análise</h2>
        <p>
        Envie um edital de credenciamento ou licitação em PDF.
        A IA analisará documentos, prazos, valores, riscos e próximos passos.
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Envie um edital PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.button("🔍 Analisar Edital"):

            with st.spinner("Analisando edital com IA..."):

                resultado = analisar_edital(
                    uploaded_file,
                    user_email
                )

                st.session_state.resultado_atual = resultado
                st.success("Análise concluída com sucesso!")
                st.rerun()

    if "resultado_atual" in st.session_state:

        resultado = st.session_state.resultado_atual
        pdf = gerar_pdf(resultado)

        st.markdown("""
        <div class="card">
            <h2>📋 Resultado da análise</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown(resultado)
        st.markdown('</div>', unsafe_allow_html=True)

        st.download_button(
            label="📄 Baixar PDF",
            data=pdf,
            file_name="relatorio_credmed_ia.pdf",
            mime="application/pdf"
        )

    if st.session_state.resultado_antigo:

        pdf_antigo = gerar_pdf(
            st.session_state.resultado_antigo
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
            <h2>📂 Análise salva</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown(st.session_state.resultado_antigo)
        st.markdown('</div>', unsafe_allow_html=True)

        st.download_button(
            label="📄 Baixar PDF da análise salva",
            data=pdf_antigo,
            file_name="analise_salva_credmed_ia.pdf",
            mime="application/pdf"
        )


elif pagina == "Radar de Oportunidades":

    tela_oportunidades()


elif pagina == "Base Inteligente":

    tela_oportunidades_salvas()


elif pagina == "Meus Alertas":

    tela_alertas(user_email)