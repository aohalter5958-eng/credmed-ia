import streamlit as st
import plotly.graph_objects as go
from collections import Counter

from auth import inicializar_sessao, tela_login, logout
from database import buscar_historico, buscar_oportunidades, supabase
from analyzer import analisar_edital
from pdf_generator import gerar_pdf
from styles import aplicar_estilo
from opportunities import tela_oportunidades
from saved_opportunities import tela_oportunidades_salvas
from alerts import tela_alertas
from professionals import tela_profissionais, buscar_profissionais
from admin import tela_admin_profissionais


ADMIN_EMAILS = [
    "aohalter5958@gmail.com"
]


st.set_page_config(
    page_title="CredMed IA",
    page_icon="🏥",
    layout="wide"
)

aplicar_estilo()
inicializar_sessao()

if st.session_state.user is None:
    tela_login()
    st.stop()

user_email = st.session_state.user
historico = buscar_historico(user_email)


def buscar_alertas_total(user_email):
    try:
        response = (
            supabase
            .table("alerts")
            .select("*")
            .eq("user_email", user_email)
            .execute()
        )
        return response.data if response.data else []
    except Exception:
        return []


def buscar_profissionais_pendentes():
    try:
        response = (
            supabase
            .table("profissionais")
            .select("*")
            .eq("status_verificacao", "pendente")
            .execute()
        )
        return response.data if response.data else []
    except Exception:
        return []


def extrair_estado(local):
    if not local:
        return "Não informado"

    if "/" in local:
        return local.split("/")[-1].strip()

    return "Não informado"


def grafico_pizza(titulo, labels, values):
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.45
            )
        ]
    )

    fig.update_layout(
        title=titulo,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=360
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_barras(titulo, labels, values):
    fig = go.Figure(
        data=[
            go.Bar(
                x=labels,
                y=values
            )
        ]
    )

    fig.update_layout(
        title=titulo,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=360
    )

    st.plotly_chart(fig, use_container_width=True)


with st.sidebar:
    st.markdown("## 🏥 CredMed IA")
    st.success(f"Logado como:\n\n{user_email}")

    paginas = [
        "Painel",
        "Radar de Oportunidades",
        "Base Inteligente",
        "Meus Alertas",
        "Marketplace Profissional"
    ]

    if user_email in ADMIN_EMAILS:
        paginas.append("Painel Admin")

    pagina = st.radio(
        "Navegação",
        paginas
    )

    if st.button("Sair"):
        logout()

    st.markdown("---")
    st.markdown("## 📂 Histórico")

    if historico:
        for item in historico:
            with st.expander(f"📄 {item['nome_arquivo'][:28]}"):
                st.caption(item["criado_em"])

                if st.button(
                    f"Abrir análise {item['id']}",
                    key=f"abrir_{item['id']}"
                ):
                    st.session_state.resultado_antigo = item["resultado"]
                    st.rerun()
    else:
        st.info("Nenhuma análise encontrada.")


if pagina == "Painel":

    oportunidades = buscar_oportunidades()
    profissionais = buscar_profissionais()
    alertas = buscar_alertas_total(user_email)
    pendentes = buscar_profissionais_pendentes()

    total_oportunidades = len(oportunidades)
    total_profissionais = len(profissionais)
    total_alertas = len(alertas)
    total_pendentes = len(pendentes)

    credenciamentos = [
        item for item in oportunidades
        if str(item.get("tipo", "")).lower() == "credenciamento"
    ]

    licitacoes = [
        item for item in oportunidades
        if str(item.get("tipo", "")).lower() in ["licitação", "licitacao"]
    ]

    excelentes = [
        item for item in oportunidades
        if "excelente" in str(item.get("relevancia", "")).lower()
        or "muito boa" in str(item.get("relevancia", "")).lower()
    ]

    st.markdown("""
    <div class="hero">
        <h1>🏥 CredMed IA</h1>
        <h3>
        Plataforma SaaS para análise inteligente de credenciamentos,
        licitações públicas, oportunidades e profissionais da saúde.
        </h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Oportunidades</div>
            <div class="metric-value">{total_oportunidades}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Profissionais</div>
            <div class="metric-value">{total_profissionais}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Alertas ativos</div>
            <div class="metric-value">{total_alertas}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Alta relevância</div>
            <div class="metric-value">{len(excelentes)}</div>
        </div>
        """, unsafe_allow_html=True)

    if user_email in ADMIN_EMAILS:
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card">
            <h2>🛡️ Controle Administrativo</h2>
            <p>
            Profissionais aguardando verificação manual:
            <strong>{total_pendentes}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h2>📊 Inteligência de Mercado</h2>
        <p>
        Visão executiva das oportunidades capturadas, profissionais cadastrados
        e movimentação da plataforma.
        </p>
    </div>
    """, unsafe_allow_html=True)

    g1, g2 = st.columns(2)

    with g1:
        grafico_pizza(
            "Credenciamentos x Licitações",
            ["Credenciamentos", "Licitações", "Outros"],
            [
                len(credenciamentos),
                len(licitacoes),
                max(
                    total_oportunidades
                    - len(credenciamentos)
                    - len(licitacoes),
                    0
                )
            ]
        )

    with g2:
        relevancias = [
            str(item.get("relevancia", "Não informado"))
            for item in oportunidades
        ]

        contagem_relevancia = Counter(relevancias)

        if contagem_relevancia:
            grafico_barras(
                "Oportunidades por relevância",
                list(contagem_relevancia.keys()),
                list(contagem_relevancia.values())
            )
        else:
            st.info("Ainda não há dados suficientes para relevância.")

    g3, g4 = st.columns(2)

    with g3:
        estados = [
            extrair_estado(item.get("local", ""))
            for item in oportunidades
        ]

        contagem_estados = Counter(estados)
        top_estados = contagem_estados.most_common(8)

        if top_estados:
            grafico_barras(
                "Estados com mais oportunidades",
                [x[0] for x in top_estados],
                [x[1] for x in top_estados]
            )
        else:
            st.info("Ainda não há dados suficientes por estado.")

    with g4:
        profissoes = [
            str(item.get("profissao", "Não informado"))
            for item in profissionais
        ]

        contagem_profissoes = Counter(profissoes)
        top_profissoes = contagem_profissoes.most_common(8)

        if top_profissoes:
            grafico_barras(
                "Profissões cadastradas",
                [x[0] for x in top_profissoes],
                [x[1] for x in top_profissoes]
            )
        else:
            st.info("Ainda não há profissionais suficientes para gráfico.")

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

elif pagina == "Marketplace Profissional":
    tela_profissionais()

elif pagina == "Painel Admin":
    if user_email in ADMIN_EMAILS:
        tela_admin_profissionais(user_email)
    else:
        st.error("Acesso negado.")