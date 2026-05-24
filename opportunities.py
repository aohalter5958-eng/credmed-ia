import requests
import streamlit as st
from datetime import date, timedelta

from smart_filters import (
    calcular_score,
    classificar_relevancia,
    oportunidade_valida
)

from database import salvar_oportunidade


PNCP_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta"


def texto_item(item):
    partes = [
        str(item.get("objetoCompra", "")),
        str(item.get("informacaoComplementar", "")),
        str(item.get("modalidadeNome", "")),
        str(item.get("situacaoCompraNome", "")),
    ]

    orgao = item.get("orgaoEntidade", {})
    unidade = item.get("unidadeOrgao", {})

    if isinstance(orgao, dict):
        partes.append(str(orgao.get("razaoSocial", "")))

    if isinstance(unidade, dict):
        partes.append(str(unidade.get("municipioNome", "")))
        partes.append(str(unidade.get("ufSigla", "")))

    return " ".join(partes).lower()


def eh_credenciamento(texto):
    return (
        "credenciamento" in texto
        or "credenciar" in texto
        or "credenciado" in texto
    )


def pegar_orgao(item):
    orgao = item.get("orgaoEntidade", {})
    if isinstance(orgao, dict):
        return orgao.get("razaoSocial", "Órgão não informado")
    return "Órgão não informado"


def pegar_local(item):
    unidade = item.get("unidadeOrgao", {})
    if isinstance(unidade, dict):
        cidade = unidade.get("municipioNome", "Cidade não informada")
        uf = unidade.get("ufSigla", "")
        return f"{cidade}/{uf}"
    return "Local não informado"


def pegar_link(item):
    orgao = item.get("orgaoEntidade", {})
    cnpj = item.get("cnpjOrgao")

    if isinstance(orgao, dict):
        cnpj = cnpj or orgao.get("cnpj")

    ano = item.get("anoCompra")
    sequencial = item.get("sequencialCompra")

    if cnpj and ano and sequencial:
        return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}"

    numero = item.get("numeroControlePNCP", "")
    return f"https://pncp.gov.br/app/editais?q={numero}"


def passa_filtros(item, tipo, palavra_chave):
    texto = texto_item(item)

    if not oportunidade_valida(texto):
        return False

    if tipo == "Credenciamento" and not eh_credenciamento(texto):
        return False

    if tipo == "Licitação" and eh_credenciamento(texto):
        return False

    if palavra_chave and palavra_chave.lower().strip() not in texto:
        return False

    return True


def consultar_pncp(estado, dias, paginas):
    resultados = []

    data_final = (
        date.today() + timedelta(days=dias)
    ).strftime("%Y%m%d")

    headers = {
        "Accept": "application/json",
        "User-Agent": "CredMed-IA/1.0"
    }

    for pagina in range(1, paginas + 1):
        params = {
            "dataFinal": data_final,
            "pagina": pagina,
            "tamanhoPagina": 50
        }

        if estado != "Todos":
            params["uf"] = estado

        try:
            resposta = requests.get(
                PNCP_URL,
                params=params,
                headers=headers,
                timeout=30
            )

            if resposta.status_code != 200:
                st.warning(f"PNCP retornou status {resposta.status_code} na página {pagina}.")
                continue

            dados = resposta.json()
            itens = dados.get("data", [])

            if not itens:
                break

            resultados.extend(itens)

        except requests.exceptions.Timeout:
            st.warning(f"O PNCP demorou demais na página {pagina}. A busca continuou.")
            break

        except Exception as erro:
            st.warning(f"Erro ao consultar PNCP na página {pagina}: {erro}")

    return resultados


def transformar_item(item):
    texto = texto_item(item)

    score = calcular_score(texto)
    relevancia = classificar_relevancia(score)

    tipo = "Credenciamento" if eh_credenciamento(texto) else "Licitação"

    return {
        "numero_controle_pncp": item.get("numeroControlePNCP"),
        "titulo": item.get("objetoCompra", "Objeto não informado"),
        "tipo": tipo,
        "relevancia": relevancia,
        "score": score,
        "orgao": pegar_orgao(item),
        "local": pegar_local(item),
        "modalidade": item.get("modalidadeNome", "Não informado"),
        "situacao": item.get("situacaoCompraNome", "Não informado"),
        "fim_propostas": item.get("dataEncerramentoProposta", "Não informado"),
        "valor_estimado": item.get("valorTotalEstimado", "Não informado"),
        "link": pegar_link(item)
    }


def renderizar_card_oportunidade(item):
    st.markdown(
        f"""
        <div style="
            background:#0f1230;
            padding:25px;
            border-radius:20px;
            margin-bottom:25px;
            border:1px solid rgba(255,255,255,0.08);
        ">
            <h2 style="color:white;">📄 {item['titulo'][:260]}</h2>
            <p><b>Tipo detectado:</b> {item['tipo']}</p>
            <p><b>Relevância:</b> {item['relevancia']}</p>
            <p><b>Score inteligente:</b> {item['score']}</p>
            <p><b>Órgão:</b> {item['orgao']}</p>
            <p><b>Local:</b> {item['local']}</p>
            <p><b>Modalidade:</b> {item['modalidade']}</p>
            <p><b>Situação:</b> {item['situacao']}</p>
            <p><b>Fim das propostas:</b> {item['fim_propostas']}</p>
            <p><b>Valor estimado:</b> R$ {item['valor_estimado']}</p>
            <a href="{item['link']}" target="_blank"
               style="display:inline-block;margin-top:12px;padding:10px 18px;background:#8b5cf6;color:white;text-decoration:none;border-radius:12px;font-weight:bold;">
               🔗 Abrir no PNCP
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )


def tela_oportunidades():
    st.title("Radar de Oportunidades")

    col1, col2 = st.columns(2)

    with col1:
        tipo = st.selectbox(
            "Tipo",
            ["Todos", "Credenciamento", "Licitação"]
        )

        estado = st.selectbox(
            "Estado",
            ["PR", "SP", "SC", "RS", "MG", "RJ", "Todos"]
        )

    with col2:
        palavra_chave = st.text_input(
            "Palavra-chave opcional",
            placeholder="Ex: médico, UPA, hospital, enfermagem..."
        )

        dias = st.slider(
            "Buscar oportunidades até quantos dias?",
            7,
            180,
            60,
            step=7
        )

    paginas = st.slider(
        "Quantidade de páginas PNCP",
        1,
        10,
        3
    )

    if st.button("🔎 Buscar oportunidades reais"):
        with st.spinner("Consultando PNCP em tempo real..."):
            itens = consultar_pncp(
                estado=estado,
                dias=dias,
                paginas=paginas
            )

        filtradas = [
            transformar_item(item)
            for item in itens
            if passa_filtros(item, tipo, palavra_chave)
        ]

        filtradas = sorted(
            filtradas,
            key=lambda x: x["score"],
            reverse=True
        )

        st.subheader("Resultado da busca")
        st.write("**Fonte:** PNCP")
        st.write(f"**Registros brutos:** {len(itens)}")
        st.write(f"**Oportunidades filtradas:** {len(filtradas)}")

        salvas = 0
        duplicadas = 0

        for item in filtradas:
            if salvar_oportunidade(item):
                salvas += 1
            else:
                duplicadas += 1

        st.success(f"✅ {salvas} oportunidades novas salvas automaticamente na Base Inteligente.")

        if duplicadas:
            st.info(f"♻️ {duplicadas} oportunidades duplicadas ignoradas.")

        if not filtradas:
            st.warning("Nenhuma oportunidade relevante encontrada.")
        else:
            for item in filtradas:
                renderizar_card_oportunidade(item)