import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
import hashlib

st.set_page_config(page_title="Monitor de Saúde Mental", layout="wide", page_icon="🧠")

# Conexão com a planilha
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vSR4W34p1g80bie4CjRdyzm1_OJliRpA0VUtnNz1D_g/edit?usp=sharing"

# Colunas fixas — sempre nesta ordem
COLUNAS = ["data", "nome", "codigo_usuario", "Humor", "Irritabilidade",
           "Bateria", "Sono", "Nevoa", "Pressao", "remedios"]

def gerar_codigo(nome, senha):
    """Gera um código único combinando nome + senha"""
    texto = f"{nome.strip().lower()}:{senha.strip()}"
    return hashlib.md5(texto.encode()).hexdigest()[:8]

def ler_dados():
    try:
        df = conn.read(spreadsheet=SHEET_URL, usecols=COLUNAS, ttl=5)
        return df.dropna(how="all")
    except:
        return pd.DataFrame(columns=COLUNAS)

def salvar_registro(dados_dict):
    df_atual = ler_dados()
    novo = pd.DataFrame([dados_dict])
    df_final = pd.concat([df_atual, novo], ignore_index=True)
    # Garante que as colunas estão na ordem certa
    for col in COLUNAS:
        if col not in df_final.columns:
            df_final[col] = ""
    df_final = df_final[COLUNAS]
    conn.update(spreadsheet=SHEET_URL, data=df_final)

# ─── TELA DE LOGIN ───────────────────────────────────────────
st.title("🧠 Monitor de Saúde Mental")

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
    st.session_state.codigo_usuario = None

if st.session_state.usuario_logado is None:
    st.subheader("Entrar no sistema")
    st.info("Use um nome fictício se preferir manter sua privacidade.")

    with st.form("login_form"):
        nome = st.text_input("Seu nome ou apelido", placeholder="Ex: Borboleta Azul")
        senha = st.text_input("Crie uma senha pessoal", type="password",
                              placeholder="Só você precisa saber")
        col1, col2 = st.columns(2)
        with col1:
            entrar = st.form_submit_button("✅ Entrar / Cadastrar")

    if entrar:
        if nome.strip() == "" or senha.strip() == "":
            st.error("Por favor, preencha nome e senha.")
        else:
            codigo = gerar_codigo(nome, senha)
            st.session_state.usuario_logado = nome.strip()
            st.session_state.codigo_usuario = codigo
            st.rerun()

    st.stop()

# ─── USUÁRIO LOGADO ──────────────────────────────────────────
nome_usuario = st.session_state.usuario_logado
codigo_usuario = st.session_state.codigo_usuario

st.sidebar.success(f"👤 Logado como: {nome_usuario}")
if st.sidebar.button("Sair"):
    st.session_state.usuario_logado = None
    st.session_state.codigo_usuario = None
    st.rerun()

# ─── MEDICAMENTOS ─────────────────────────────────────────────
st.subheader("💊 Gestão de Medicamentos")
df_todos = ler_dados()

# Busca último registro de remédios deste usuário
remedios_salvos = ""
if not df_todos.empty and "codigo_usuario" in df_todos.columns:
    df_user = df_todos[df_todos["codigo_usuario"] == codigo_usuario]
    if not df_user.empty and "remedios" in df_user.columns:
        remedios_salvos = df_user["remedios"].dropna().iloc[-1] if not df_user["remedios"].dropna().empty else ""

remedios_input = st.text_area(
    "Remédios que você toma (Nome, Dosagem, Horário):",
    value=remedios_salvos,
    placeholder="Ex: Sertralina 50mg - manhã\nClonazepam 0,5mg - noite"
)

# ─── QUESTIONÁRIO DIÁRIO ──────────────────────────────────────
st.markdown("---")
st.subheader("📝 Como você está hoje?")

with st.form("diario_form"):
    c1, c2 = st.columns(2)
    with c1:
        humor = st.select_slider("😊 Humor (Triste → Feliz)", options=[1,2,3,4,5], value=3)
        irritabilidade = st.select_slider("😤 Irritabilidade (Calmo → Irritado)", options=[1,2,3,4,5], value=1)
        bateria = st.select_slider("🔋 Bateria Social (Esgotado → Sociável)", options=[1,2,3,4,5], value=3)
    with c2:
        sono = st.select_slider("😴 Qualidade do Sono (Péssimo → Ótimo)", options=[1,2,3,4,5], value=3)
        nevoa = st.select_slider("🧩 Foco Mental (Confuso → Claro)", options=[1,2,3,4,5], value=3)
        pressao = st.select_slider("🌡️ Pressão Interna (Tranquilo → Exausto)", options=[1,2,3,4,5], value=1)

    atualizar_rem = st.checkbox("Quero atualizar meus remédios junto com este registro")
    submit = st.form_submit_button("💾 Salvar Registro de Hoje")

if submit:
    dados = {
        "data": str(date.today()),
        "nome": nome_usuario,
        "codigo_usuario": codigo_usuario,
        "Humor": humor,
        "Irritabilidade": irritabilidade,
        "Bateria": bateria,
        "Sono": sono,
        "Nevoa": nevoa,
        "Pressao": pressao,
        "remedios": remedios_input if atualizar_rem else remedios_salvos
    }
    try:
        salvar_registro(dados)
        st.balloons()
        st.success("✅ Registro salvo com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

# ─── RELATÓRIO E ALERTAS ──────────────────────────────────────
st.markdown("---")
st.subheader("📊 Análise de Padrões e Relatórios")

if st.button("📈 Gerar Relatório dos Últimos 7 Dias"):
    df_todos = ler_dados()

    if df_todos.empty or "codigo_usuario" not in df_todos.columns:
        st.warning("Ainda não há dados na planilha.")
    else:
        df_user = df_todos[df_todos["codigo_usuario"] == codigo_usuario].copy()

        if df_user.empty:
            st.markdown("""
            <div style="background:#ffcccc;padding:20px;border-radius:10px;border:2px solid #cc0000;text-align:center">
                <h3 style="color:#cc0000">⚠️ Sem registros encontrados</h3>
                <p>Você ainda não fez nenhum registro. Comece hoje!</p>
            </div>""", unsafe_allow_html=True)
        else:
            df_user["data"] = pd.to_datetime(df_user["data"])
            limite = pd.to_datetime(date.today() - timedelta(days=7))
            df_7dias = df_user[df_user["data"] >= limite]

            if df_7dias.empty:
                st.markdown("""
                <div style="background:#ffcccc;padding:20px;border-radius:10px;border:2px solid #cc0000;text-align:center">
                    <h3 style="color:#cc0000">⚠️ Sem participação esta semana</h3>
                    <p>Nenhum registro nos últimos 7 dias. Tente manter a constância!</p>
                </div>""", unsafe_allow_html=True)
            else:
                # Gráfico
                metricas = ["Humor", "Sono", "Pressao", "Irritabilidade", "Bateria", "Nevoa"]
                metricas_existentes = [m for m in metricas if m in df_7dias.columns]
                fig = px.line(df_7dias, x="data", y=metricas_existentes,
                              title=f"Evolução de {nome_usuario} — Últimos 7 dias",
                              markers=True, labels={"data": "Data", "value": "Nível (1-5)"})
                fig.update_layout(yaxis=dict(range=[0,6], tickmode="linear", dtick=1))
                st.plotly_chart(fig, use_container_width=True)

                registros = len(df_7dias)
                if registros < 7:
                    st.warning(f"Você registrou {registros} de 7 dias esta semana.")
                else:
                    st.success("🎉 Semana completa! Todos os 7 dias registrados.")

                # ─── ALERTA DE BURNOUT ────────────────────────────────
                alertas = []
                if len(df_7dias) >= 3:
                    if df_7dias["Pressao"].tail(3).mean() >= 4:
                        alertas.append("Pressão interna persistentemente alta")
                    if df_7dias["Humor"].tail(3).mean() <= 2:
                        alertas.append("Humor consistentemente baixo")
                    if df_7dias["Sono"].tail(3).mean() <= 2:
                        alertas.append("Qualidade de sono muito baixa")
                    if df_7dias["Irritabilidade"].tail(3).mean() >= 4:
                        alertas.append("Irritabilidade elevada nos últimos dias")

                if alertas:
                    itens = "".join([f"<li>{a}</li>" for a in alertas])
                    st.markdown(f"""
                    <div style="background:#fffacc;padding:20px;border-radius:10px;border:2px solid #e6c200;margin-top:15px">
                        <h3 style="color:#7a6000;margin-top:0">⚠️ Atenção — Sinais de Alerta Detectados</h3>
                        <p style="color:#444"><b>Para o profissional de saúde:</b> O paciente <b>{nome_usuario}</b> apresentou os seguintes padrões:</p>
                        <ul style="color:#444">{itens}</ul>
                        <p style="color:#444">Recomenda-se revisão dos procedimentos terapêuticos.</p>
                    </div>""", unsafe_allow_html=True)
