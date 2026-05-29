import streamlit as st
from database import supabase


def salvar_profissional(dados):
    supabase.table("profissionais").insert(dados).execute()


def buscar_profissionais():
    response = (
        supabase
        .table("profissionais")
        .select("*")
        .eq("status_verificacao", "aprovado")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data if response.data else []


def card_profissional(item):
    st.markdown(
        f"""
        <div style="
            background:#0f1230;
            padding:25px;
            border-radius:20px;
            margin-bottom:20px;
            border:1px solid rgba(255,255,255,0.08);
        ">

        <h2 style="color:white;">
            👨‍⚕️ {item.get("nome", "Profissional")}
        </h2>

        <p><b>Profissão:</b> {item.get("profissao", "-")}</p>

        <p><b>Especialidade:</b> {item.get("especialidade", "-")}</p>

        <p><b>Conselho:</b> {item.get("conselho", "-")}</p>

        <p><b>Registro:</b> {item.get("numero_registro", "-")}</p>

        <p><b>Estado:</b> {item.get("estado", "-")}</p>

        <p><b>Cidade:</b> {item.get("cidade", "-")}</p>

        <p><b>Disponibilidade:</b> {item.get("disponibilidade", "-")}</p>

        <p><b>Tipos contrato:</b> {item.get("tipos_contrato", "-")}</p>

        <p><b>Valor plantão:</b> {item.get("valor_plantao", "-")}</p>

        <p><b>Experiência:</b> {item.get("experiencia", "-")}</p>

        <p><b>Palavras-chave:</b> {item.get("palavras_chave", "-")}</p>

        <p><b>Currículo:</b> {item.get("curriculo", "-")}</p>

        <p><b>Telefone:</b> {item.get("telefone", "-")}</p>

        <p><b>Email:</b> {item.get("email", "-")}</p>

        </div>
        """,
        unsafe_allow_html=True
    )


def tela_profissionais():
    st.title("🏥 Marketplace Profissional")

    st.write(
        "Cadastre profissionais da saúde para credenciamentos e oportunidades."
    )

    with st.form("cadastro_profissional"):

        nome = st.text_input("Nome completo")

        profissao = st.selectbox(
            "Profissão",
            [
                "Médico",
                "Enfermeiro",
                "Fisioterapeuta",
                "Psicólogo",
                "Farmacêutico",
                "Biomédico",
                "Dentista",
                "Técnico de Enfermagem",
                "Outro"
            ]
        )

        especialidade = st.text_input("Especialidade")

        conselho = st.text_input(
            "Conselho profissional (CRM, COREN, etc)"
        )

        numero_registro = st.text_input(
            "Número do registro profissional"
        )

        estado = st.text_input("Estado")

        cidade = st.text_input("Cidade")

        telefone = st.text_input("Telefone")

        email = st.text_input("Email")

        disponibilidade = st.selectbox(
            "Disponibilidade",
            [
                "Imediata",
                "Plantões",
                "PJ",
                "CLT",
                "Parcial"
            ]
        )

        tipos_contrato = st.text_input(
            "Tipos de contrato"
        )

        valor_plantao = st.text_input(
            "Valor médio do plantão"
        )

        experiencia = st.text_area(
            "Experiência profissional"
        )

        palavras_chave = st.text_input(
            "Palavras-chave"
        )

        curriculo = st.text_area(
            "Resumo do currículo"
        )

        salvar = st.form_submit_button(
            "💾 Salvar profissional"
        )

        if salvar:

            dados = {
                "nome": nome,
                "profissao": profissao,
                "especialidade": especialidade,
                "conselho": conselho,
                "numero_registro": numero_registro,
                "estado": estado,
                "cidade": cidade,
                "telefone": telefone,
                "email": email,
                "disponibilidade": disponibilidade,
                "tipos_contrato": tipos_contrato,
                "valor_plantao": valor_plantao,
                "experiencia": experiencia,
                "palavras_chave": palavras_chave,
                "curriculo": curriculo
            }

            salvar_profissional(dados)

            st.success("✅ Profissional salvo com sucesso!")

    st.divider()

    st.subheader("Profissionais cadastrados")

    profissionais = buscar_profissionais()

    st.write(f"Total cadastrados: {len(profissionais)}")

    if not profissionais:
        st.warning("Nenhum profissional cadastrado.")
    else:
        for item in profissionais:
            card_profissional(item)