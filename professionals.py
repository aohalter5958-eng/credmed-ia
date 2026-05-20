import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def salvar_profissional(dados):
    supabase.table("professionals").insert(dados).execute()


def buscar_profissionais():
    response = (
        supabase.table("professionals")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    return response.data


def tela_profissionais():

    st.markdown("## 👩‍⚕️ Marketplace de Profissionais da Saúde")

    st.write(
        "Cadastro e busca de profissionais para empresas que atuam em credenciamentos e licitações."
    )

    aba1, aba2 = st.tabs(
        [
            "Cadastrar profissional",
            "Buscar profissionais"
        ]
    )

    with aba1:

        st.markdown("### Novo profissional")

        with st.form("form_profissional"):

            nome = st.text_input("Nome completo")

            profissao = st.selectbox(
                "Profissão",
                [
                    "Médico",
                    "Enfermeiro",
                    "Técnico de Enfermagem",
                    "Fisioterapeuta",
                    "Psicólogo",
                    "Farmacêutico",
                    "Dentista",
                    "Biomédico",
                    "Radiologista",
                    "Nutricionista",
                    "Outro"
                ]
            )

            especialidade = st.text_input(
                "Especialidade",
                placeholder="Ex: Clínico Geral, Pediatria, UTI, PSF..."
            )

            col1, col2 = st.columns(2)

            with col1:
                estado = st.selectbox(
                    "Estado",
                    [
                        "PR",
                        "SP",
                        "SC",
                        "RS",
                        "MG",
                        "RJ",
                        "Todos"
                    ]
                )

            with col2:
                cidade = st.text_input("Cidade")

            telefone = st.text_input("Telefone / WhatsApp")

            email = st.text_input("E-mail")

            experiencia = st.text_area(
                "Experiência profissional",
                placeholder="Descreva experiência em UPA, UBS, hospital, plantões, SUS..."
            )

            valor_plantao = st.text_input(
                "Valor desejado por plantão / hora",
                placeholder="Ex: R$ 1.200 por plantão"
            )

            disponibilidade = st.selectbox(
                "Disponibilidade",
                [
                    "Imediata",
                    "Durante a semana",
                    "Finais de semana",
                    "Plantões noturnos",
                    "A combinar"
                ]
            )

            enviar = st.form_submit_button(
                "💾 Salvar profissional"
            )

        if enviar:

            dados = {
                "nome": nome,
                "profissao": profissao,
                "especialidade": especialidade,
                "estado": estado,
                "cidade": cidade,
                "telefone": telefone,
                "email": email,
                "experiencia": experiencia,
                "valor_plantao": valor_plantao,
                "disponibilidade": disponibilidade
            }

            salvar_profissional(dados)

            st.success("Profissional cadastrado com sucesso!")

    with aba2:

        st.markdown("### Buscar profissionais")

        profissionais = buscar_profissionais()

        filtro_profissao = st.selectbox(
            "Filtrar por profissão",
            [
                "Todos",
                "Médico",
                "Enfermeiro",
                "Técnico de Enfermagem",
                "Fisioterapeuta",
                "Psicólogo",
                "Farmacêutico",
                "Dentista",
                "Biomédico",
                "Radiologista",
                "Nutricionista",
                "Outro"
            ]
        )

        filtro_estado = st.selectbox(
            "Filtrar por estado",
            [
                "Todos",
                "PR",
                "SP",
                "SC",
                "RS",
                "MG",
                "RJ"
            ]
        )

        busca = st.text_input(
            "Buscar por nome, cidade ou especialidade"
        )

        resultados = profissionais

        if filtro_profissao != "Todos":
            resultados = [
                p for p in resultados
                if p["profissao"] == filtro_profissao
            ]

        if filtro_estado != "Todos":
            resultados = [
                p for p in resultados
                if p["estado"] == filtro_estado
            ]

        if busca:
            termo = busca.lower()

            resultados = [
                p for p in resultados
                if termo in str(p.get("nome", "")).lower()
                or termo in str(p.get("cidade", "")).lower()
                or termo in str(p.get("especialidade", "")).lower()
            ]

        st.write(f"Profissionais encontrados: {len(resultados)}")

        for p in resultados:

            with st.container(border=True):

                st.subheader(f"👤 {p['nome']}")

                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Profissão:** {p['profissao']}")
                    st.write(f"**Especialidade:** {p['especialidade']}")
                    st.write(f"**Local:** {p['cidade']}/{p['estado']}")
                    st.write(f"**Disponibilidade:** {p['disponibilidade']}")

                with col2:
                    st.write(f"**Telefone:** {p['telefone']}")
                    st.write(f"**E-mail:** {p['email']}")
                    st.write(f"**Valor:** {p['valor_plantao']}")

                st.write("**Experiência:**")
                st.write(p["experiencia"])