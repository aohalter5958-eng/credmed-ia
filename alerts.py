import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def salvar_alerta(user_email, tipo, estado, palavra_chave, frequencia):
    return (
        supabase.table("alerts")
        .insert({
            "user_email": user_email,
            "tipo": tipo,
            "estado": estado,
            "palavra_chave": palavra_chave,
            "frequencia": frequencia
        })
        .execute()
    )


def buscar_alertas(user_email):
    response = (
        supabase.table("alerts")
        .select("*")
        .eq("user_email", user_email)
        .order("id", desc=True)
        .execute()
    )
    return response.data


def buscar_oportunidades_salvas():
    response = (
        supabase.table("opportunities")
        .select("*")
        .order("id", desc=True)
        .limit(300)
        .execute()
    )
    return response.data


def alerta_combina(alerta, oportunidade):
    tipo_alerta = alerta.get("tipo", "Todos")
    estado_alerta = alerta.get("estado", "Todos")
    palavra = str(alerta.get("palavra_chave", "")).lower().strip()

    texto_oportunidade = " ".join([
        str(oportunidade.get("titulo", "")),
        str(oportunidade.get("orgao", "")),
        str(oportunidade.get("local", "")),
        str(oportunidade.get("modalidade", "")),
        str(oportunidade.get("situacao", "")),
        str(oportunidade.get("tipo", ""))
    ]).lower()

    if tipo_alerta != "Todos":
        if str(oportunidade.get("tipo", "")) != tipo_alerta:
            return False

    if estado_alerta != "Todos":
        local = str(oportunidade.get("local", ""))
        if f"/{estado_alerta}" not in local:
            return False

    if palavra:
        if palavra not in texto_oportunidade:
            return False

    return True


def card_oportunidade_alerta(oportunidade):
    with st.container(border=True):
        st.subheader(f"📄 {oportunidade.get('titulo', 'Sem título')}")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Tipo:** {oportunidade.get('tipo')}")
            st.write(f"**Relevância:** {oportunidade.get('relevancia')}")
            st.write(f"**Score:** {oportunidade.get('score')}")
            st.write(f"**Órgão:** {oportunidade.get('orgao')}")
            st.write(f"**Local:** {oportunidade.get('local')}")

        with col2:
            st.write(f"**Modalidade:** {oportunidade.get('modalidade')}")
            st.write(f"**Situação:** {oportunidade.get('situacao')}")
            st.write(f"**Fim propostas:** {oportunidade.get('fim_propostas')}")
            st.write(f"**Valor estimado:** R$ {oportunidade.get('valor_estimado')}")

        link = oportunidade.get("link")

        if link:
            st.link_button("🔗 Abrir oportunidade", link)


def tela_alertas(user_email):
    st.markdown("## 🚨 Meus Alertas Inteligentes")

    st.write(
        "Crie alertas por tipo, estado e palavra-chave. "
        "O sistema compara seus alertas com a Base Inteligente do CredMed IA."
    )

    with st.form("novo_alerta"):
        tipo = st.selectbox(
            "Tipo de oportunidade",
            ["Todos", "Credenciamento", "Licitação"]
        )

        estado = st.selectbox(
            "Estado",
            ["Todos", "PR", "SP", "SC", "RS", "MG", "RJ"]
        )

        palavra_chave = st.text_input(
            "Palavra-chave",
            placeholder="Ex: médico, enfermagem, UPA, hospital, laboratório..."
        )

        frequencia = st.selectbox(
            "Frequência desejada",
            ["Diário", "A cada 12 horas", "Semanal"]
        )

        enviar = st.form_submit_button("💾 Salvar alerta")

    if enviar:
        salvar_alerta(
            user_email=user_email,
            tipo=tipo,
            estado=estado,
            palavra_chave=palavra_chave,
            frequencia=frequencia
        )

        st.success("Alerta salvo com sucesso!")

    st.markdown("---")

    alertas = buscar_alertas(user_email)
    oportunidades = buscar_oportunidades_salvas()

    st.markdown("## 📡 Alertas cadastrados")

    if not alertas:
        st.warning("Nenhum alerta cadastrado ainda.")
        return

    for alerta in alertas:
        with st.container(border=True):
            st.subheader(f"🚨 {alerta.get('tipo', 'Todos')}")

            st.write(f"**Estado:** {alerta.get('estado')}")
            st.write(f"**Palavra-chave:** {alerta.get('palavra_chave')}")
            st.write(f"**Frequência:** {alerta.get('frequencia')}")

            oportunidades_compativeis = [
                oportunidade
                for oportunidade in oportunidades
                if alerta_combina(alerta, oportunidade)
            ]

            st.write(
                f"**Oportunidades compatíveis encontradas:** "
                f"{len(oportunidades_compativeis)}"
            )

            if oportunidades_compativeis:
                with st.expander("Ver oportunidades compatíveis"):
                    for oportunidade in oportunidades_compativeis:
                        card_oportunidade_alerta(oportunidade)