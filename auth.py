import streamlit as st
from database import supabase
from streamlit_cookies_controller import CookieController


cookie_controller = CookieController()


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


def inicializar_sessao():
    if "user" not in st.session_state:
        st.session_state.user = None

    if "resultado_antigo" not in st.session_state:
        st.session_state.resultado_antigo = None

    if st.session_state.user is None:
        email_salvo = cookie_controller.get("credmed_user_email")

        if email_salvo:
            st.session_state.user = email_salvo


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
                    cookie_controller.set(
                        "credmed_user_email",
                        response.user.email
                    )

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

    try:
        cookie_controller.remove("credmed_user_email")
    except Exception:
        pass

    st.rerun()