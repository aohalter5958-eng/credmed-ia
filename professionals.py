import re
import streamlit as st
from database import supabase, upload_curriculo_pdf


def salvar_profissional(dados):
    supabase.table("profissionais").insert(dados).execute()


def atualizar_profissional(profissional_id, dados):
    supabase.table("profissionais").update(dados).eq("id", profissional_id).execute()


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


def buscar_meu_perfil(user_email):
    response = (
        supabase
        .table("profissionais")
        .select("*")
        .eq("user_email", user_email)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


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
    curriculo_pdf = item.get("curriculo_pdf", "")

    st.markdown(
        f"""
        <div style="
            background:#0f1230;
            padding:25px;
            border-radius:20px;
            margin-bottom:20px;
            border:1px solid rgba(255,255,255,0.08);
        ">

        <h2 style="color:white;">👨‍⚕️ {nome}</h2>

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
        <p><b>Currículo resumido:</b> {item.get("curriculo", "-")}</p>
        <p><b>Telefone:</b> {telefone}</p>
        <p><b>Email:</b> {email}</p>

        </div>
        """,
        unsafe_allow_html=True
    )

    if curriculo_pdf:
        st.link_button(
            "📄 Baixar currículo PDF",
            curriculo_pdf,
            use_container_width=True
        )

    if telefone:
        st.link_button(
            "📱 Chamar no WhatsApp",
            gerar_link_whatsapp(telefone, nome),
            use_container_width=True
        )

    if email:
        st.link_button(
            "📧 Enviar Email",
            gerar_link_email(email, nome),
            use_container_width=True
        )


def formulario_profissional(dados_existentes=None):
    if dados_existentes is None:
        dados_existentes = {}

    nome = st.text_input(
        "Nome completo",
        value=dados_existentes.get("nome", "")
    )

    opcoes_profissao = [
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

    profissao_atual = dados_existentes.get("profissao", "Enfermeiro")

    if profissao_atual not in opcoes_profissao:
        profissao_atual = "Outro"

    profissao = st.selectbox(
        "Profissão",
        opcoes_profissao,
        index=opcoes_profissao.index(profissao_atual)
    )

    especialidade = st.text_input(
        "Especialidade",
        value=dados_existentes.get("especialidade", "")
    )

    conselho = st.text_input(
        "Conselho profissional (CRM, COREN, etc)",
        value=dados_existentes.get("conselho", "")
    )

    numero_registro = st.text_input(
        "Número do registro profissional",
        value=dados_existentes.get("numero_registro", "")
    )

    estado = st.text_input(
        "Estado",
        value=dados_existentes.get("estado", "")
    )

    cidade = st.text_input(
        "Cidade",
        value=dados_existentes.get("cidade", "")
    )

    telefone = st.text_input(
        "Telefone/WhatsApp",
        value=dados_existentes.get("telefone", ""),
        placeholder="Ex: 44999999999"
    )

    email = st.text_input(
        "Email",
        value=dados_existentes.get("email", "")
    )

    opcoes_disponibilidade = [
        "Imediata",
        "Plantões",
        "PJ",
        "CLT",
        "Parcial"
    ]

    disponibilidade_atual = dados_existentes.get(
        "disponibilidade",
        "Imediata"
    )

    if disponibilidade_atual not in opcoes_disponibilidade:
        disponibilidade_atual = "Imediata"

    disponibilidade = st.selectbox(
        "Disponibilidade",
        opcoes_disponibilidade,
        index=opcoes_disponibilidade.index(disponibilidade_atual)
    )

    tipos_contrato = st.text_input(
        "Tipos de contrato",
        value=dados_existentes.get("tipos_contrato", "")
    )

    valor_plantao = st.text_input(
        "Valor médio do plantão",
        value=dados_existentes.get("valor_plantao", "")
    )

    experiencia = st.text_area(
        "Experiência profissional",
        value=dados_existentes.get("experiencia", "")
    )

    palavras_chave = st.text_input(
        "Palavras-chave",
        value=dados_existentes.get("palavras_chave", "")
    )

    curriculo = st.text_area(
        "Resumo do currículo",
        value=dados_existentes.get("curriculo", "")
    )

    arquivo_curriculo = st.file_uploader(
        "Anexar/Atualizar currículo em PDF",
        type=["pdf"]
    )

    return {
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
        "arquivo_curriculo": arquivo_curriculo
    }


def tela_meu_perfil(user_email):
    st.title("👤 Meu Perfil Profissional")

    st.write(
        "Cadastre ou atualize suas informações profissionais. "
        "Toda alteração voltará para análise administrativa."
    )

    perfil = buscar_meu_perfil(user_email)

    if perfil:
        status = perfil.get("status_verificacao", "pendente")

        if status == "verificado":
            st.success("✅ Seu perfil está verificado e visível no Marketplace.")
        elif status == "pendente":
            st.warning("🟡 Seu perfil está aguardando verificação administrativa.")
        elif status == "recusado":
            st.error("🔴 Seu perfil foi recusado. Atualize as informações e envie novamente.")
        else:
            st.info(f"Status atual: {status}")

        curriculo_pdf = perfil.get("curriculo_pdf")

        if curriculo_pdf:
            st.link_button(
                "📄 Ver currículo PDF atual",
                curriculo_pdf,
                use_container_width=True
            )

    else:
        st.info("Você ainda não possui perfil profissional cadastrado.")

    with st.form("form_meu_perfil"):

        dados_form = formulario_profissional(perfil)

        salvar = st.form_submit_button("💾 Salvar meu perfil")

        if salvar:

            curriculo_pdf_url = perfil.get("curriculo_pdf") if perfil else None

            if dados_form["arquivo_curriculo"] is not None:
                curriculo_pdf_url = upload_curriculo_pdf(
                    dados_form["arquivo_curriculo"],
                    dados_form["nome"]
                )

            dados = {
                "user_email": user_email,
                "nome": dados_form["nome"],
                "profissao": dados_form["profissao"],
                "especialidade": dados_form["especialidade"],
                "conselho": dados_form["conselho"],
                "numero_registro": dados_form["numero_registro"],
                "estado": dados_form["estado"],
                "cidade": dados_form["cidade"],
                "telefone": dados_form["telefone"],
                "email": dados_form["email"],
                "disponibilidade": dados_form["disponibilidade"],
                "tipos_contrato": dados_form["tipos_contrato"],
                "valor_plantao": dados_form["valor_plantao"],
                "experiencia": dados_form["experiencia"],
                "palavras_chave": dados_form["palavras_chave"],
                "curriculo": dados_form["curriculo"],
                "curriculo_pdf": curriculo_pdf_url,
                "status_verificacao": "pendente"
            }

            if perfil:
                atualizar_profissional(
                    perfil.get("id"),
                    dados
                )

                st.success(
                    "✅ Perfil atualizado com sucesso! "
                    "Ele voltou para análise administrativa."
                )

            else:
                salvar_profissional(dados)

                st.success(
                    "✅ Perfil criado com sucesso! "
                    "Ele ficará pendente até validação administrativa."
                )

            st.rerun()


def tela_profissionais(user_email=None):
    st.title("🏥 Marketplace Profissional")

    st.write(
        "Profissionais verificados da saúde disponíveis para credenciamentos e oportunidades."
    )

    profissionais = buscar_profissionais()

    st.write(f"Total cadastrados: {len(profissionais)}")

    if not profissionais:
        st.warning("Nenhum profissional cadastrado.")
    else:
        for item in profissionais:
            card_profissional(item)