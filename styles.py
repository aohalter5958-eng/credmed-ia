import streamlit as st


def aplicar_estilo():

    st.markdown("""

    <style>

    .stApp {
        background: #050816;
        color: white;
    }

    html, body, p, label, span, div,
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }

    .main .block-container {
        padding-top: 2rem;
        max-width: 1300px;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #0b1020,
                #111827
            );

        border-right:
            1px solid #1f2937;
    }

    .stTextInput input {

        background:
            #111827 !important;

        color:
            white !important;

        border-radius:
            12px;
    }

    .card {

        background:
            linear-gradient(
                180deg,
                #111827,
                #0f172a
            );

        border:
            1px solid #1f2937;

        border-radius:
            20px;

        padding:
            28px;

        box-shadow:
            0 0 20px rgba(0,0,0,0.3);

        margin-bottom:
            20px;
    }

    .metric-card {

        background:
            linear-gradient(
                180deg,
                #111827,
                #0b1020
            );

        border:
            1px solid #1f2937;

        border-radius:
            18px;

        padding:
            22px;

        text-align:
            center;
    }

    .metric-title {

        color:
            #9ca3af !important;

        font-size:
            14px;
    }

    .metric-value {

        color:
            white !important;

        font-size:
            32px;

        font-weight:
            800;
    }

    .hero {

        background:

            radial-gradient(
                circle at top left,
                rgba(124,58,237,0.4),
                transparent 40%
            ),

            linear-gradient(
                135deg,
                #0f172a,
                #111827
            );

        border:
            1px solid #1f2937;

        border-radius:
            25px;

        padding:
            45px;

        margin-bottom:
            30px;
    }

    .result-box {

        background:
            #111827;

        border:
            1px solid #1f2937;

        border-radius:
            20px;

        padding:
            25px;

        color:
            white;
    }

    .stButton > button {

        background:
            linear-gradient(
                90deg,
                #2563eb,
                #7c3aed
            ) !important;

        color:
            white !important;

        border:
            none !important;

        border-radius:
            12px !important;

        padding:
            12px 20px !important;

        font-weight:
            700 !important;
    }

    .stDownloadButton > button {

        background:
            linear-gradient(
                90deg,
                #16a34a,
                #15803d
            ) !important;

        color:
            white !important;

        border:
            none !important;

        border-radius:
            12px !important;

        padding:
            12px 20px !important;

        font-weight:
            700 !important;
    }

    </style>

    """, unsafe_allow_html=True)