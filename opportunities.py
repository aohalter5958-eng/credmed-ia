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
            <h2 style="color:white;">
                📄 {item.get('titulo', 'Sem título')}
            </h2>

            <p><b>Tipo detectado:</b> {item.get('tipo')}</p>
            <p><b>Relevância:</b> {item.get('relevancia')}</p>
            <p><b>Score inteligente:</b> {item.get('score')}</p>
            <p><b>Órgão:</b> {item.get('orgao')}</p>
            <p><b>Local:</b> {item.get('local')}</p>
            <p><b>Modalidade:</b> {item.get('modalidade')}</p>
            <p><b>Situação:</b> {item.get('situacao')}</p>
            <p><b>Fim das propostas:</b> {item.get('fim_propostas')}</p>
            <p><b>Valor estimado:</b> R$ {item.get('valor_estimado')}</p>

            <a href="{item.get('link')}" target="_blank">
                🔗 Abrir oportunidade
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )


def consultar_pncp(paginas=3):
    oportunidades = []

    for pagina in range(1, paginas + 1):
        try:
            url = (
                "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
                f"?pagina={pagina}&tamanhoPagina=20"
            )

            response = requests.get(url, timeout=30)

            if response.status_code != 200:
                continue

            dados = response.json()

            lista = dados.get("data", [])

            for item in lista:

                titulo = item.get("objetoCompra", "")

                oportunidade = {
                    "numero_controle_pncp": item.get("numeroControlePNCP"),
                    "titulo": titulo,
                    "tipo": "Credenciamento",
                    "relevancia": "Alta",
                    "score": 60,
                    "orgao": item.get("orgaoEntidade", {}).get("razaoSocial"),
                    "local": item.get("unidadeOrgao", {}).get("municipioNome"),
                    "modalidade": item.get("modalidadeNome"),
                    "situacao": item.get("situacaoCompraNome"),
                    "fim_propostas": item.get("dataEncerramentoProposta"),
                    "valor_estimado": item.get("valorTotalEstimado"),
                    "link": item.get("linkSistemaOrigem")
                }

                if oportunidade_valida(titulo):
                    oportunidades.append(oportunidade)

        except Exception as erro:
            st.warning(
                f"O PNCP demorou demais na página {pagina}. "
                f"A busca continuou com os dados encontrados."
            )

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

        with st.spinner("Consultando PNCP em tempo real..."):

            oportunidades = consultar_pncp(paginas)

            st.subheader("Resultado da busca")

            st.write(f"Fonte: PNCP")
            st.write(f"Registros brutos: {len(oportunidades)}")

            oportunidades_filtradas = []

            for item in oportunidades:

                if oportunidade_valida(item["titulo"]):
                    oportunidades_filtradas.append(item)

            st.write(
                f"Oportunidades filtradas: "
                f"{len(oportunidades_filtradas)}"
            )

            salvas = 0
            duplicadas = 0

            for item in oportunidades_filtradas:

                sucesso = salvar_oportunidade(item)

                if sucesso:
                    salvas += 1
                else:
                    duplicadas += 1

            st.success(
                f"✅ {salvas} oportunidades novas salvas "
                f"automaticamente na Base Inteligente."
            )

            if duplicadas > 0:
                st.info(
                    f"♻️ {duplicadas} oportunidades "
                    f"duplicadas foram ignoradas."
                )

            if not oportunidades_filtradas:
                st.warning(
                    "Nenhuma oportunidade relevante encontrada."
                )

            else:
                for item in oportunidades_filtradas:
                    renderizar_card_oportunidade(item)