import re
import streamlit as st
from database import supabase


def salvar_profissional(dados):
    supabase.table("profissionais").insert(dados).execute()


def buscar_profissionais():
    response = (
        supabase
        .table("profissionais")
        .select("*")
        .eq("status_verificacao", "verificado")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data if response.data else []


def limpar_telefone(telefone):
    if not telefone:
        return ""

    numero = re.sub(r"\D", "", telefone)

    if numero.startswith("55"):
        return numero

    return "55" + numero


def gerar_link_whatsapp(telefone, nome):
    numero = limpar_telefone(telefone)

    mensagem = (
        f"Olá, {nome}. Encontrei seu perfil no CredMed IA "
        f"e gostaria de conversar sobre uma oportunidade na área da saúde."
    )

    return f"https://wa.me/{numero}?text={mensagem}"


def gerar_link_email(email, nome):
    assunto = "Oportunidade profissional - CredMed IA"

    corpo = (
        f"Olá, {nome}.\n\n"
        f"Encontrei seu perfil no CredMed IA e gostaria de conversar "
        f"sobre uma oportunidade na área da saúde.\n\n"
        f"Aguardo seu retorno."
    )

    return f"mailto:{email}?subject={assunto}&body={corpo}"


def card_profissional(item):
    nome = item.get("nome", "Profissional")
    telefone = item.get("telefone", "")
    email = item.get("email", "")

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
            👨‍⚕️ {nome}
        </h2>

        <p><b>Status:</b> ✅ Profissional verificado</p>

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

        <p><b>Telefone:</b> {telefone}</p>

        <p><b>Email:</b> {email}</p>

        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if telefone:
            st.link_button(
                "📱 Chamar no WhatsApp",
                gerar_link_whatsapp(telefone, nome)
            )

    with col2:
        if email:
            st.link_button(
                "📧 Enviar Email",
                gerar_link_email(email, nome)
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

        telefone = st.text_input(
            "Telefone/WhatsApp",
            placeholder="Ex: 44999999999"
        )

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
                "curriculo": curriculo,
                "status_verificacao": "pendente"
            }

            salvar_profissional(dados)

            st.success(
                "✅ Cadastro enviado com sucesso! "
                "O profissional ficará pendente até validação administrativa."
            )

    st.divider()

    st.subheader("Profissionais cadastrados")

    profissionais = buscar_profissionais()

    st.write(f"Total cadastrados: {len(profissionais)}")

    if not profissionais:
        st.warning("Nenhum profissional cadastrado.")
    else:
        for item in profissionais:
            card_profissional(item)