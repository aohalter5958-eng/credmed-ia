import streamlit as st


def tela_oportunidades():

    st.markdown("""
    <div class="card">
        <h2>📡 Radar de Oportunidades</h2>
        <p>
        Encontre credenciamentos e licitações da área da saúde
        em todo o Brasil.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        tipo = st.selectbox(
            "Tipo de oportunidade",
            [
                "Credenciamento",
                "Licitação"
            ]
        )

        estado = st.selectbox(
            "Estado",
            [
                "Paraná",
                "São Paulo",
                "Santa Catarina",
                "Rio Grande do Sul",
                "Minas Gerais"
            ]
        )

    with col2:

        cidade = st.text_input(
            "Cidade"
        )

        especialidade = st.selectbox(
            "Especialidade",
            [
                "Clínico Geral",
                "Enfermagem",
                "Fisioterapia",
                "Psicologia",
                "Farmácia",
                "Radiologia",
                "Odontologia"
            ]
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔎 Buscar oportunidades"):

        st.success(
            f"""
            Busca iniciada para:

            • Tipo: {tipo}
            • Estado: {estado}
            • Cidade: {cidade}
            • Especialidade: {especialidade}
            """
        )

        st.markdown("<br>", unsafe_allow_html=True)

        oportunidades_fake = [

            {
                "titulo": "Credenciamento Médico UPA",
                "orgao": "Prefeitura Municipal",
                "cidade": cidade if cidade else "Maringá",
                "valor": "R$ 180.000/mês",
                "status": "Aberto"
            },

            {
                "titulo": "Licitação Serviços Hospitalares",
                "orgao": "Hospital Regional",
                "cidade": cidade if cidade else "Curitiba",
                "valor": "R$ 2.400.000",
                "status": "Próximo do vencimento"
            }

        ]

        for item in oportunidades_fake:

            st.markdown(f"""

            <div class="card">

            <h3>📄 {item['titulo']}</h3>

            <p><b>Órgão:</b> {item['orgao']}</p>

            <p><b>Cidade:</b> {item['cidade']}</p>

            <p><b>Valor:</b> {item['valor']}</p>

            <p><b>Status:</b> {item['status']}</p>

            </div>

            """, unsafe_allow_html=True)