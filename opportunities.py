import streamlit as st
import requests

from smart_filters import oportunidade_valida
from database import salvar_oportunidade


def renderizar_card_oportunidade(item):

    st.markdown(
        f"""
        <div style="
            background: #0f1230;
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.08);
        ">

            <h2 style="
                color:white;
                margin-bottom:20px;
            ">
                📄 {item.get('titulo', 'Sem título')}
            </h2>

            <p><b>Tipo detectado:</b> {item.get('tipo')}</p>

            <p>
                <b>Relevância:</b>
                🟢 {item.get('relevancia')}
            </p>

            <p>
                <b>Score inteligente:</b>
                {item.get('score')}
            </p>

            <p>
                <b>Órgão:</b>
                {item.get('orgao')}
            </p>

            <p>
                <b>Local:</b>
                {item.get('local')}
            </p>

            <p>
                <b>Modalidade:</b>
                {item.get('modalidade')}
            </p>

            <p>
                <b>Situação:</b>
                {item.get('situacao')}
            </p>

            <p>
                <b>Fim das propostas:</b>
                {item.get('fim_propostas')}
            </p>

            <p>
                <b>Valor estimado:</b>
                R$ {item.get('valor_estimado')}
            </p>

            <a
                href="{item.get('link')}"
                target="_blank"
                style="
                    display:inline-block;
                    margin-top:15px;
                    padding:10px 18px;
                    background:#8b5cf6;
                    color:white;
                    text-decoration:none;
                    border-radius:12px;
                    font-weight:bold;
                "
            >
                🔗 Abrir oportunidade
            </a>

        </div>
        """,
        unsafe_allow_html=True
    )


def consultar_pncp(paginas=3):

    oportunidades = []

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    for pagina in range(1, paginas + 1):

        try:

            url = (
                "https://pncp.gov.br/api/search/"
                f"?pagina={pagina}"
                "&tamanhoPagina=20"
            )

            response = requests.get(
                url,
                headers=headers,
                timeout=60
            )

            if response.status_code != 200:
                continue

            dados = response.json()

            lista = dados.get("items", [])

            for item in lista:

                titulo = item.get("titulo", "")

                oportunidade = {

                    "numero_controle_pncp":
                        item.get("id"),

                    "titulo":
                        titulo,

                    "tipo":
                        "Credenciamento",

                    "relevancia":
                        "Excelente",

                    "score":
                        60,

                    "orgao":
                        item.get("orgao"),

                    "local":
                        item.get("municipio"),

                    "modalidade":
                        item.get("modalidade"),

                    "situacao":
                        item.get("situacao"),

                    "fim_propostas":
                        item.get("dataEncerramento"),

                    "valor_estimado":
                        item.get("valor"),

                    "link":
                        item.get("link")
                }

                if oportunidade_valida(titulo):

                    oportunidades.append(
                        oportunidade
                    )

        except Exception as erro:

            st.warning(
                f"O PNCP demorou demais na página "
                f"{pagina}. "
                f"A busca continuou com os dados "
                f"encontrados."
            )

            print("ERRO PNCP:")
            print(erro)

    return oportunidades


def tela_oportunidades():

    st.title("Radar de Oportunidades")

    paginas = st.slider(
        "Quantidade de páginas PNCP",
        1,
        10,
        3
    )

    if st.button("🔎 Buscar oportunidades reais"):

        with st.spinner(
            "Consultando PNCP em tempo real..."
        ):

            oportunidades = consultar_pncp(
                paginas
            )

            st.subheader(
                "Resultado da busca"
            )

            st.write("Fonte: PNCP")

            st.write(
                f"Registros brutos: "
                f"{len(oportunidades)}"
            )

            oportunidades_filtradas = []

            for item in oportunidades:

                if oportunidade_valida(
                    item["titulo"]
                ):

                    oportunidades_filtradas.append(
                        item
                    )

            st.write(
                f"Oportunidades filtradas: "
                f"{len(oportunidades_filtradas)}"
            )

            salvas = 0
            duplicadas = 0

            for item in oportunidades_filtradas:

                sucesso = salvar_oportunidade(
                    item
                )

                if sucesso:
                    salvas += 1

                else:
                    duplicadas += 1

            st.success(
                f"✅ {salvas} oportunidades "
                f"novas salvas automaticamente "
                f"na Base Inteligente."
            )

            if duplicadas > 0:

                st.info(
                    f"♻️ {duplicadas} oportunidades "
                    f"duplicadas foram ignoradas."
                )

            if not oportunidades_filtradas:

                st.warning(
                    "Nenhuma oportunidade "
                    "relevante encontrada."
                )

            else:

                for item in oportunidades_filtradas:

                    renderizar_card_oportunidade(
                        item
                    )