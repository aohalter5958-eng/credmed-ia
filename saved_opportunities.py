import streamlit as st
from database import buscar_oportunidades


def card_oportunidade(item):

    with st.container(border=True):

        st.subheader(f"📄 {item['titulo']}")

        col1, col2 = st.columns(2)

        with col1:

            st.write(f"**Tipo:** {item['tipo']}")

            st.write(f"**Relevância:** {item['relevancia']}")

            st.write(f"**Score:** {item['score']}")

            st.write(f"**Órgão:** {item['orgao']}")

            st.write(f"**Local:** {item['local']}")

        with col2:

            st.write(f"**Modalidade:** {item['modalidade']}")

            st.write(f"**Situação:** {item['situacao']}")

            st.write(f"**Fim propostas:** {item['fim_propostas']}")

            st.write(f"**Valor estimado:** R$ {item['valor_estimado']}")

        st.link_button(
            "🔗 Abrir oportunidade",
            item["link"]
        )


def tela_oportunidades_salvas():

    st.markdown("## 🧠 Base Inteligente CredMed IA")

    st.write(
        "Oportunidades reais armazenadas automaticamente pelo radar."
    )

    oportunidades = buscar_oportunidades()

    st.write(f"Total armazenado: {len(oportunidades)}")

    if not oportunidades:

        st.warning(
            "Nenhuma oportunidade salva ainda."
        )

        return

    filtro_tipo = st.selectbox(
        "Filtrar tipo",
        [
            "Todos",
            "Credenciamento",
            "Licitação"
        ]
    )

    filtro_relevancia = st.selectbox(
        "Filtrar relevância",
        [
            "Todas",
            "Excelente",
            "Alta",
            "Média",
            "Baixa"
        ]
    )

    oportunidades_filtradas = oportunidades

    if filtro_tipo != "Todos":

        oportunidades_filtradas = [
            x for x in oportunidades_filtradas
            if x["tipo"] == filtro_tipo
        ]

    if filtro_relevancia != "Todas":

        oportunidades_filtradas = [
            x for x in oportunidades_filtradas
            if x["relevancia"] == filtro_relevancia
        ]

    st.write(
        f"Resultados encontrados: "
        f"{len(oportunidades_filtradas)}"
    )

    for item in oportunidades_filtradas:

        card_oportunidade(item)