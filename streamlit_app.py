import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import hashlib

st.set_page_config(page_title="Monitor de Saúde Mental", layout="wide", page_icon="🧠")

# ─── ESTILO VISUAL (TEMA BRANCO) ─────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    div[data-testid="metric-container"] {
        background: #ffffff;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .alerta-vermelho {
        background: #fff0f0;
        border: 2px solid #ff4444;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    .alerta-amarelo {
        background: #fffbe6;
        border: 2px solid #ffcc00;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    .card-info {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e0e0e0;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── CONFIGURAÇÕES ────────────────────────────────────────────
CORES_METRICAS = {
    "Humor":         "#2196F3",
    "Sono":          "#9C27B0",
    "Pressao":       "#F44336",
    "Irritabilidade":"#FF9800",
    "Bateria":       "#4CAF50",
    "Nevoa":         "#00BCD4"
}

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vSR4W34p1g80bie4CjRdyzm1_OJliRpA0VUtnNz1D_g/edit?usp=sharing"
COLUNAS = ["data", "nome", "codigo_usuario", "Humor", "Irritabilidade",
           "Bateria", "Sono", "Nevoa", "Pressao", "remedios"]

# ─── FUNÇÕES AUXILIARES ───────────────────────────────────────
def gerar_codigo(nome, senha):
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
    for col in COLUNAS:
        if col not in df_final.columns:
            df_final[col] = ""
    df_final = df_final[COLUNAS]
    conn.update(spreadsheet=SHEET_URL, data=df_final)

def detectar_alertas(df):
    alertas = []
    gravidade = 0
    if len(df) >= 3:
        if df["Pressao"].tail(3).mean() >= 4:
            alertas.append(("🌡️", "Pressão interna persistentemente alta"))
            gravidade += 2
        if df["Humor"].tail(3).mean() <= 2:
            alertas.append(("😔", "Humor consistentemente baixo"))
            gravidade += 2
        if df["Sono"].tail(3).mean() <= 2:
            alertas.append(("😴", "Qualidade de sono muito baixa"))
            gravidade += 1
        if df["Irritabilidade"].tail(3).mean() >= 4:
            alertas.append(("😤", "Irritabilidade elevada nos últimos dias"))
            gravidade += 1
        if df["Bateria"].tail(3).mean() <= 2:
            alertas.append(("🔋", "Bateria social esgotada"))
            gravidade += 1
        if df["Nevoa"].tail(3).mean() <= 2:
            alertas.append(("🧩", "Névoa mental persistente — dificuldade de foco"))
            gravidade += 1
    return alertas, gravidade

# ─── TELA DE LOGIN ────────────────────────────────────────────
st.title("🧠 Monitor de Saúde Mental")

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
    st.session_state.codigo_usuario = None

if st.session_state.usuario_logado is None:
    st.subheader("Entrar no sistema")
    st.info("Use um nome fictício se preferir manter sua privacidade.")

    with st.form("login_form"):
        nome = st.text_input("Seu nome ou apelido", placeholder="Ex: Borboleta Azul")
        senha = st.text_input("Sua senha pessoal", type="password",
                              placeholder="Só você precisa saber")
        entrar = st.form_submit_button("✅ Entrar / Cadastrar")

    if entrar:
        if nome.strip() == "" or senha.strip() == "":
            st.error("Por favor, preencha nome e senha.")
        else:
            st.session_state.usuario_logado = nome.strip()
            st.session_state.codigo_usuario = gerar_codigo(nome, senha)
            st.rerun()

    st.stop()

# ─── USUÁRIO LOGADO ───────────────────────────────────────────
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

remedios_salvos = ""
if not df_todos.empty and "codigo_usuario" in df_todos.columns:
    df_user_rem = df_todos[df_todos["codigo_usuario"] == codigo_usuario]
    if not df_user_rem.empty:
        ultimos = df_user_rem["remedios"].dropna()
        if not ultimos.empty:
            remedios_salvos = ultimos.iloc[-1]

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
        humor = st.select_slider("😊 Humor (Triste → Feliz)",
                                  options=[1,2,3,4,5], value=3)
        irritabilidade = st.select_slider("😤 Irritabilidade (Calmo → Irritado)",
                                           options=[1,2,3,4,5], value=1)
        bateria = st.select_slider("🔋 Bateria Social (Esgotado → Sociável)",
                                    options=[1,2,3,4,5], value=3)
    with c2:
        sono = st.select_slider("😴 Qualidade do Sono (Péssimo → Ótimo)",
                                 options=[1,2,3,4,5], value=3)
        nevoa = st.select_slider("🧩 Foco Mental (Confuso → Claro)",
                                  options=[1,2,3,4,5], value=3)
        pressao = st.select_slider("🌡️ Pressão Interna (Tranquilo → Exausto)",
                                    options=[1,2,3,4,5], value=1)

    atualizar_rem = st.checkbox("Quero atualizar meus remédios junto com este registro")
    submit = st.form_submit_button("💾 Salvar Registro de Hoje")

if submit:
    dados = {
        "data":            str(date.today()),
        "nome":            nome_usuario,
        "codigo_usuario":  codigo_usuario,
        "Humor":           humor,
        "Irritabilidade":  irritabilidade,
        "Bateria":         bateria,
        "Sono":            sono,
        "Nevoa":           nevoa,
        "Pressao":         pressao,
        "remedios":        remedios_input if atualizar_rem else remedios_salvos
    }
    try:
        salvar_registro(dados)
        st.balloons()
        st.success("✅ Registro salvo com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

# ─── RELATÓRIO SEMANAL ────────────────────────────────────────
st.markdown("---")
st.subheader("📊 Relatório Semanal")

if st.button("📈 Gerar Relatório dos Últimos 7 Dias"):
    df_todos = ler_dados()

    if df_todos.empty or "codigo_usuario" not in df_todos.columns:
        st.warning("Ainda não há dados na planilha.")
        st.stop()

    df_user = df_todos[df_todos["codigo_usuario"] == codigo_usuario].copy()

    if df_user.empty:
        st.markdown("""
        <div class="alerta-vermelho">
            <h3 style="color:#cc0000">⚠️ Sem registros encontrados</h3>
            <p style="color:#333">Você ainda não fez nenhum registro. Comece hoje!</p>
        </div>""", unsafe_allow_html=True)
        st.stop()

    df_user["data"] = pd.to_datetime(df_user["data"])
    limite = pd.to_datetime(date.today() - timedelta(days=7))
    df_7dias = df_user[df_user["data"] >= limite].copy()

    if df_7dias.empty:
        st.markdown("""
        <div class="alerta-vermelho">
            <h3 style="color:#cc0000">⚠️ Sem participação esta semana</h3>
            <p style="color:#333">Nenhum registro nos últimos 7 dias. Tente manter a constância!</p>
        </div>""", unsafe_allow_html=True)
        st.stop()

    # ── Cards de médias da semana ────────────────────────────
    st.markdown("### 📋 Resumo da Semana")
    metricas = ["Humor", "Sono", "Pressao", "Irritabilidade", "Bateria", "Nevoa"]
    emojis   = {"Humor":"😊", "Sono":"😴", "Pressao":"🌡️",
                "Irritabilidade":"😤", "Bateria":"🔋", "Nevoa":"🧩"}

    cols = st.columns(len(metricas))
    for i, m in enumerate(metricas):
        if m in df_7dias.columns:
            media = df_7dias[m].mean()
            delta = (df_7dias[m].iloc[-1] - df_7dias[m].iloc[0]
                     if len(df_7dias) > 1 else 0)
            cols[i].metric(
                label=f"{emojis[m]} {m}",
                value=f"{media:.1f} / 5",
                delta=f"{delta:+.0f} vs início"
            )

    # ── Gráfico de linhas ────────────────────────────────────
    st.markdown("### 📈 Evolução ao Longo da Semana")

    df_long = df_7dias[["data"] + metricas].melt(
        id_vars="data", value_vars=metricas,
        var_name="Métrica", value_name="Nível"
    )

    fig = go.Figure()
    for metrica in metricas:
        df_m = df_long[df_long["Métrica"] == metrica]
        fig.add_trace(go.Scatter(
            x=df_m["data"],
            y=df_m["Nível"],
            mode="lines+markers",
            name=metrica,
            line=dict(color=CORES_METRICAS.get(metrica, "#333333"), width=2.5),
            marker=dict(size=8)
        ))

    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#f8f9fa",
        font=dict(color="#333333"),
        legend=dict(bgcolor="#ffffff", bordercolor="#e0e0e0"),
        xaxis=dict(gridcolor="#e0e0e0", title="Data"),
        yaxis=dict(gridcolor="#e0e0e0", range=[0, 6],
                   tickmode="linear", dtick=1, title="Nível (1-5)"),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Gráfico radar ────────────────────────────────────────
    st.markdown("### 🎯 Perfil Geral da Semana")

    medias = [df_7dias[m].mean() for m in metricas]
    fig_radar = go.Figure(go.Scatterpolar(
        r=medias + [medias[0]],
        theta=metricas + [metricas[0]],
        fill="toself",
        fillcolor="rgba(33, 150, 243, 0.15)",
        line=dict(color="#2196F3", width=2),
        marker=dict(size=6)
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="#ffffff",
            radialaxis=dict(visible=True, range=[0, 5],
                            gridcolor="#e0e0e0", color="#555555"),
            angularaxis=dict(gridcolor="#e0e0e0", color="#333333")
        ),
        paper_bgcolor="#f8f9fa",
        font=dict(color="#333333"),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── Participação ─────────────────────────────────────────
    registros = len(df_7dias)
    if registros < 7:
        st.warning(f"📅 Você registrou {registros} de 7 dias esta semana.")
    else:
        st.success("🎉 Semana completa! Todos os 7 dias registrados.")

    # ── Alertas de burnout ───────────────────────────────────
    alertas, gravidade = detectar_alertas(df_7dias)

    if alertas:
        itens_html = "".join([
            f'<li style="margin:8px 0"><b>{e}</b> {txt}</li>'
            for e, txt in alertas
        ])
        nivel     = "ALTO RISCO" if gravidade >= 4 else "ATENÇÃO"
        cor_borda = "#ff4444"    if gravidade >= 4 else "#ffcc00"
        cor_fundo = "#fff0f0"    if gravidade >= 4 else "#fffbe6"
        cor_titulo= "#cc0000"    if gravidade >= 4 else "#7a6000"

        st.markdown(f"""
        <div style="background:{cor_fundo};
                    border:2px solid {cor_borda};
                    border-radius:12px;
                    padding:20px;
                    margin-top:15px">
            <h3 style="color:{cor_titulo};margin-top:0">⚠️ {nivel} — Sinais Detectados</h3>
            <p style="color:#444">
                <b>Para o profissional de saúde:</b>
                O paciente <b>{nome_usuario}</b> apresentou os seguintes padrões:
            </p>
            <ul style="color:#444">{itens_html}</ul>
            <p style="color:#888;font-size:0.9em">
                Recomenda-se revisão dos procedimentos terapêuticos.
            </p>
        </div>""", unsafe_allow_html=True)
    else:
        st.success("✅ Nenhum sinal de alerta detectado esta semana. Continue assim!")
