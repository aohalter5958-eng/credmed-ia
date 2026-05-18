import streamlit as st

from auth import (
    inicializar_sessao,
    tela_login,
    logout
)

from database import buscar_historico

from analyzer import analisar_edital

from pdf_generator import gerar_pdf

from styles import aplicar_estilo

from opportunities import tela_oportunidades


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

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.markdown("## 🏥 CredMed IA")

    st.success(
        f"Logado como:\n\n{user_email}"
    )

    pagina = st.radio(
        "Navegação",
        [
            "Dashboard",
            "Radar de Oportunidades"
        ]
    )

    if st.button("Logout"):
        logout()

    st.markdown("---")

    st.markdown("## 📂 Histórico")

    if historico:

        for item in historico:

            with st.expander(
                f"📄 {item['nome_arquivo'][:28]}"
            ):

                st.caption(
                    item["criado_em"]
                )

                if st.button(
                    f"Abrir análise {item['id']}",
                    key=f"abrir_{item['id']}"
                ):

                    st.session_state.resultado_antigo = item["resultado"]

                    st.rerun()

    else:

        st.info(
            "Nenhuma análise encontrada."
        )


# =====================================
# DASHBOARD
# =====================================

if pagina == "Dashboard":

    st.markdown("""

    <div class="hero">

        <h1>🏥 CredMed IA</h1>

        <h3>
        Plataforma SaaS premium para análise inteligente
        de credenciamentos médicos e editais públicos.
        </h3>

    </div>

    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(f"""

        <div class="metric-card">

            <div class="metric-title">
            Total de análises
            </div>

            <div class="metric-value">
            {len(historico)}
            </div>

        </div>

        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""

        <div class="metric-card">

            <div class="metric-title">
            Plano atual
            </div>

            <div class="metric-value">
            FREE
            </div>

        </div>

        """, unsafe_allow_html=True)

    with col3:

        st.markdown("""

        <div class="metric-card">

            <div class="metric-title">
            Status IA
            </div>

            <div class="metric-value">
            ONLINE
            </div>

        </div>

        """, unsafe_allow_html=True)

    with col4:

        st.markdown("""

        <div class="metric-card">

            <div class="metric-title">
            Plataforma
            </div>

            <div class="metric-value">
            BETA
            </div>

        </div>

        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""

    <div class="card">

        <h2>📄 Nova análise</h2>

        <p>
        Envie um edital PDF e receba uma análise
        estratégica completa feita por IA.
        </p>

    </div>

    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Envie um edital PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.button("🔍 Analisar Edital"):

            with st.spinner(
                "Analisando edital..."
            ):

                resultado = analisar_edital(
                    uploaded_file,
                    user_email
                )

                st.session_state.resultado_atual = resultado

                st.success(
                    "Análise concluída!"
                )

                st.rerun()

    if "resultado_atual" in st.session_state:

        resultado = st.session_state.resultado_atual

        pdf = gerar_pdf(resultado)

        st.markdown("""

        <div class="card">

            <h2>
            📋 Resultado da análise
            </h2>

        </div>

        """, unsafe_allow_html=True)

        st.markdown(
            '<div class="result-box">',
            unsafe_allow_html=True
        )

        st.markdown(resultado)

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

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

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )

        st.markdown("""

        <div class="card">

            <h2>
            📂 Análise salva
            </h2>

        </div>

        """, unsafe_allow_html=True)

        st.markdown(
            '<div class="result-box">',
            unsafe_allow_html=True
        )

        st.markdown(
            st.session_state.resultado_antigo
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        st.download_button(
            label="📄 Baixar PDF da análise salva",
            data=pdf_antigo,
            file_name="analise_salva_credmed_ia.pdf",
            mime="application/pdf"
        )

# =====================================
# OPORTUNIDADES
# =====================================

elif pagina == "Radar de Oportunidades":

    tela_oportunidades()