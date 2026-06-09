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


def buscar_empresas_pendentes():
    response = (
        supabase
        .table("empresas")
        .select("*")
        .eq("status_verificacao", "pendente")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data if response.data else []


def atualizar_status_profissional(profissional_id, status, observacao, admin_email):
    supabase.table("profissionais").update({
        "status_verificacao": status,
        "observacao_verificacao": observacao,
        "verificado_em": datetime.now().isoformat(),
        "verificado_por": admin_email
    }).eq("id", profissional_id).execute()


def atualizar_status_empresa(empresa_id, status, observacao, admin_email):
    supabase.table("empresas").update({
        "status_verificacao": status,
        "observacao_verificacao": observacao,
        "verificado_em": datetime.now().isoformat(),
        "verificado_por": admin_email
    }).eq("id", empresa_id).execute()


def tela_admin_profissionais(admin_email):
    st.title("🛡️ Painel Admin")

    aba1, aba2 = st.tabs([
        "👨‍⚕️ Profissionais Pendentes",
        "🏢 Empresas Pendentes"
    ])

    with aba1:
        st.subheader("Verificação de Profissionais")

        pendentes = buscar_profissionais_pendentes()

        st.metric("Profissionais aguardando verificação", len(pendentes))

        if not pendentes:
            st.success("Nenhum profissional pendente no momento.")
        else:
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

                    curriculo_pdf = item.get("curriculo_pdf")
                    if curriculo_pdf:
                        st.link_button(
                            "📄 Ver currículo PDF",
                            curriculo_pdf,
                            use_container_width=True
                        )

                    observacao = st.text_area(
                        "Observação da verificação",
                        key=f"obs_prof_{item.get('id')}"
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(
                            "✅ Aprovar profissional",
                            key=f"aprovar_prof_{item.get('id')}"
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
                            key=f"recusar_prof_{item.get('id')}"
                        ):
                            atualizar_status_profissional(
                                item.get("id"),
                                "recusado",
                                observacao,
                                admin_email
                            )
                            st.warning("Profissional recusado.")
                            st.rerun()

    with aba2:
        st.subheader("Verificação de Empresas")

        empresas = buscar_empresas_pendentes()

        st.metric("Empresas aguardando verificação", len(empresas))

        if not empresas:
            st.success("Nenhuma empresa pendente no momento.")
        else:
            for item in empresas:
                nome_empresa = (
                    item.get("nome_empresa")
                    or item.get("nome_fantasia")
                    or item.get("razao_social")
                    or "Empresa"
                )

                with st.container(border=True):
                    st.subheader(f"🏢 {nome_empresa}")

                    st.write(f"**Razão Social:** {item.get('razao_social', '-')}")
                    st.write(f"**Nome Fantasia:** {item.get('nome_fantasia', '-')}")
                    st.write(f"**CNPJ:** {item.get('cnpj', '-')}")
                    st.write(f"**Responsável:** {item.get('responsavel', '-')}")
                    st.write(f"**Telefone:** {item.get('telefone', '-')}")
                    st.write(f"**Email:** {item.get('email', '-')}")
                    st.write(f"**Estado:** {item.get('estado', '-')}")
                    st.write(f"**Cidade:** {item.get('cidade', '-')}")
                    st.write(f"**Site/Rede social:** {item.get('site', '-')}")
                    st.write(
                        f"**Especialidades procuradas:** "
                        f"{item.get('especialidades_procuradas', '-')}"
                    )
                    st.write(
                        f"**Quantidade aproximada de profissionais:** "
                        f"{item.get('quantidade_profissionais', '-')}"
                    )
                    st.write(f"**Descrição:** {item.get('descricao', '-')}")

                    observacao = st.text_area(
                        "Observação da verificação da empresa",
                        key=f"obs_emp_{item.get('id')}"
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(
                            "✅ Aprovar empresa",
                            key=f"aprovar_emp_{item.get('id')}"
                        ):
                            atualizar_status_empresa(
                                item.get("id"),
                                "verificado",
                                observacao,
                                admin_email
                            )
                            st.success("Empresa aprovada.")
                            st.rerun()

                    with col2:
                        if st.button(
                            "❌ Recusar empresa",
                            key=f"recusar_emp_{item.get('id')}"
                        ):
                            atualizar_status_empresa(
                                item.get("id"),
                                "recusado",
                                observacao,
                                admin_email
                            )
                            st.warning("Empresa recusada.")
                            st.rerun()