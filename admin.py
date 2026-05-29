import streamlit as st
from datetime import datetime
from database import supabase


def buscar_profissionais_pendentes():
    response = (
        supabase
        .table("profissionais")
        .select("*")
        .eq("status_verificacao", "pendente")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data if response.data else []


def atualizar_status_profissional(
    profissional_id,
    status,
    observacao,
    admin_email
):
    supabase.table("profissionais").update({
        "status_verificacao": status,
        "observacao_verificacao": observacao,
        "verificado_em": datetime.now().isoformat(),
        "verificado_por": admin_email
    }).eq("id", profissional_id).execute()


def tela_admin_profissionais(admin_email):
    st.title("🛡️ Painel Admin")

    st.write(
        "Área restrita para verificação manual de profissionais cadastrados."
    )

    pendentes = buscar_profissionais_pendentes()

    st.metric(
        "Profissionais aguardando verificação",
        len(pendentes)
    )

    if not pendentes:
        st.success("Nenhum profissional pendente no momento.")
        return

    for item in pendentes:
        with st.container(border=True):
            st.subheader(f"👨‍⚕️ {item.get('nome', 'Profissional')}")

            st.write(f"**Profissão:** {item.get('profissao', '-')}")
            st.write(f"**Especialidade:** {item.get('especialidade', '-')}")
            st.write(f"**Conselho:** {item.get('conselho', '-')}")
            st.write(f"**Registro:** {item.get('numero_registro', '-')}")
            st.write(f"**Estado:** {item.get('estado', '-')}")
            st.write(f"**Cidade:** {item.get('cidade', '-')}")
            st.write(f"**Experiência:** {item.get('experiencia', '-')}")
            st.write(f"**Telefone:** {item.get('telefone', '-')}")
            st.write(f"**Email:** {item.get('email', '-')}")

            observacao = st.text_area(
                "Observação da verificação",
                key=f"obs_{item.get('id')}"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "✅ Aprovar profissional",
                    key=f"aprovar_{item.get('id')}"
                ):
                    atualizar_status_profissional(
                        item.get("id"),
                        "verificado",
                        observacao,
                        admin_email
                    )

                    st.success("Profissional aprovado.")
                    st.rerun()

            with col2:
                if st.button(
                    "❌ Recusar profissional",
                    key=f"recusar_{item.get('id')}"
                ):
                    atualizar_status_profissional(
                        item.get("id"),
                        "recusado",
                        observacao,
                        admin_email
                    )

                    st.warning("Profissional recusado.")
                    st.rerun()