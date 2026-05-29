import streamlit as st
from database import supabase


def login_usuario(email, senha):
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": senha
    })


def cadastrar_usuario(email, senha):
    return supabase.auth.sign_up({
        "email": email,
        "password": senha
    })


def pegar_usuario_da_url():
    try:
        email = st.query_params.get("user")

        if isinstance(email, list):
            return email[0]

        return email

    except Exception:
        return None


def salvar_usuario_na_url(email):
    try:
        st.query_params["user"] = email
    except Exception:
        pass


def limpar_usuario_da_url():
    try:
        if "user" in st.query_params:
            del st.query_params["user"]
    except Exception:
        pass


def inicializar_sessao():
    if "user" not in st.session_state:
        st.session_state.user = None

    if "resultado_antigo" not in st.session_state:
        st.session_state.resultado_antigo = None

    if st.session_state.user is None:
        email_url = pegar_usuario_da_url()

        if email_url:
            st.session_state.user = email_url


def tela_login():
    st.markdown("""
    <div class="hero">
        <h1>🏥 CredMed IA</h1>
        <h3>Plataforma SaaS premium para análise inteligente de credenciamentos médicos e editais públicos.</h3>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Cadastro"])

    with tab1:
        st.subheader("Entrar")

        login_email = st.text_input("E-mail", key="login_email")
        login_password = st.text_input("Senha", type="password", key="login_password")

        lembrar_login = st.checkbox(
            "Manter-me conectado neste navegador",
            value=True
        )

        if st.button("Entrar"):
            try:
                response = login_usuario(login_email, login_password)

                st.session_state.user = response.user.email

                if lembrar_login:
                    salvar_usuario_na_url(response.user.email)

                st.rerun()

            except Exception:
                st.error("Email ou senha inválidos")

    with tab2:
        st.subheader("Criar conta")

        signup_email = st.text_input("E-mail", key="signup_email")
        signup_password = st.text_input("Senha", type="password", key="signup_password")

        if st.button("Criar Conta"):
            try:
                cadastrar_usuario(signup_email, signup_password)
                st.success("Conta criada com sucesso!")
            except Exception as e:
                st.error(str(e))

    st.stop()


def logout():
    st.session_state.user = None
    st.session_state.resultado_antigo = None

    limpar_usuario_da_url()

    st.rerun()