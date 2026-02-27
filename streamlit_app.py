import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, timedelta
import plotly.graph_objects as go
import plotly.express as px
import hashlib
import numpy as np

st.set_page_config(page_title="Monitor de Saúde Mental", layout="wide", page_icon="🧠")

# ─── ESTILO VISUAL ────────────────────────────────────────────
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
</style>
""", unsafe_allow_html=True)

# ─── CONFIGURAÇÕES ────────────────────────────────────────────
CORES_METRICAS = {
    "Humor":          "#2196F3",
    "Sono":           "#9C27B0",
    "Pressao":        "#F44336",
    "Irritabilidade": "#FF9800",
    "Bateria":        "#4CAF50",
    "Nevoa":          "#00BCD4"
}
METRICAS = ["Humor", "Sono", "Pressao", "Irritabilidade", "Bateria", "Nevoa"]
EMOJIS   = {"Humor":"😊","Sono":"😴","Pressao":"🌡️",
            "Irritabilidade":"😤","Bateria":"🔋","Nevoa":"🧩"}

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vSR4W34p1g80bie4CjRdyzm1_OJliRpA0VUtnNz1D_g/edit?usp=sharing"
COLUNAS   = ["data", "nome", "codigo_usuario", "Humor", "Irritabilidade",
             "Bateria", "Sono", "Nevoa", "Pressao", "remedios"]

# ─── FUNÇÕES ──────────────────────────────────────────────────
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

def calcular_risco_burnout(df):
    if df.empty:
        return 0, "Sem dados"
    pontos = 0
    total  = 0
    pesos = {"Pressao": (True,  2.0),
             "Humor":   (False, 2.0),
             "Sono":    (False, 1.5),
             "Irritabilidade": (True, 1.5),
             "Bateria": (False, 1.0),
             "Nevoa":   (False, 1.0)}
    for col, (direto, peso) in pesos.items():
        if col in df.columns:
            media = df[col].tail(5).mean()
            val   = (media / 5) if direto else ((5 - media) / 5)
            pontos += val * peso
            total  += peso
    risco = round((pontos / total) * 100) if total > 0 else 0
    if risco >= 70:
        nivel = "🔴 Alto Risco"
    elif risco >= 40:
        nivel = "🟡 Atenção"
    else:
        nivel = "🟢 Estável"
    return risco, nivel

def detectar_padroes_semanais(df):
    if len(df) < 7:
        return []
    dias_pt = {0:"Segunda",1:"Terça",2:"Quarta",
               3:"Quinta",4:"Sexta",5:"Sábado",6:"Domingo"}
    df = df.copy()
    df["dia_semana"] = df["data"].dt.dayofweek
    padroes = []
    for metrica in ["Humor", "Sono", "Pressao"]:
        if metrica not in df.columns:
            continue
        media_geral = df[metrica].mean()
        por_dia = df.groupby("dia_semana")[metrica].mean()
        for dia_num, media_dia in por_dia.items():
            if media_dia < media_geral * 0.75 and metrica in ["Humor","Sono"]:
                padroes.append(f"📉 Toda **{dias_pt[dia_num]}** o {EMOJIS[metrica]} {metrica} costuma ser mais baixo")
            if media_dia > media_geral * 1.25 and metrica == "Pressao":
                padroes.append(f"📈 Toda **{dias_pt[dia_num]}** a {EMOJIS['Pressao']} Pressão costuma ser mais alta")
    return padroes

def calcular_correlacoes(df):
    if len(df) < 5:
        return []
    insights = []
    pares = [
        ("Sono",   "Humor",         "positiva", "Quando o sono melhora, o humor tende a melhorar também"),
        ("Pressao","Humor",          "negativa", "Quando a pressão aumenta, o humor tende a cair"),
        ("Pressao","Irritabilidade", "positiva", "Pressão alta está ligada ao aumento de irritabilidade"),
        ("Sono",   "Nevoa",          "positiva", "Sono ruim está associado a mais névoa mental"),
        ("Bateria","Humor",          "positiva", "Baixa bateria social coincide com queda no humor"),
    ]
    for col1, col2, tipo, descricao in pares:
        if col1 not in df.columns or col2 not in df.columns:
            continue
        corr = df[col1].corr(df[col2])
        if tipo == "positiva" and corr > 0.5:
            insights.append(f"🔗 {descricao} (força: {corr:.2f})")
        elif tipo == "negativa" and corr < -0.5:
            insights.append(f"🔗 {descricao} (força: {abs(corr):.2f})")
    return insights

def comparar_semanas(df_user):
    """Divide o histórico em semanas e compara as médias"""
    if len(df_user) < 7:
        return None
    df_user = df_user.copy().sort_values("data")
    df_user["semana"] = df_user["data"].dt.isocalendar().week.astype(str) + \
                        "/" + df_user["data"].dt.year.astype(str)
    resumo = df_user.groupby("semana")[METRICAS].mean().round(2).reset_index()
    return resumo

# ─── LOGIN ────────────────────────────────────────────────────
st.title("🧠 Monitor de Saúde Mental")

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
    st.session_state.codigo_usuario = None

if st.session_state.usuario_logado is None:
    st.subheader("Entrar no sistema")
    st.info("Use um nome fictício se preferir manter sua privacidade.")
    with st.form("login_form"):
        nome  = st.text_input("Seu nome ou apelido", placeholder="Ex: Borboleta Azul")
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

nome_usuario   = st.session_state.usuario_logado
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
        humor          = st.select_slider("😊 Humor (Triste → Feliz)",             options=[1,2,3,4,5], value=3)
        irritabilidade = st.select_slider("😤 Irritabilidade (Calmo → Irritado)",  options=[1,2,3,4,5], value=1)
        bateria        = st.select_slider("🔋 Bateria Social (Esgotado → Sociável)",options=[1,2,3,4,5], value=3)
    with c2:
        sono    = st.select_slider("😴 Qualidade do Sono (Péssimo → Ótimo)",   options=[1,2,3,4,5], value=3)
        nevoa   = st.select_slider("🧩 Foco Mental (Confuso → Claro)",          options=[1,2,3,4,5], value=3)
        pressao = st.select_slider("🌡️ Pressão Interna (Tranquilo → Exausto)",  options=[1,2,3,4,5], value=1)
    atualizar_rem = st.checkbox("Quero atualizar meus remédios junto com este registro")
    submit = st.form_submit_button("💾 Salvar Registro de Hoje")

if submit:
    dados = {
        "data":           str(date.today()),
        "nome":           nome_usuario,
        "codigo_usuario": codigo_usuario,
        "Humor":          humor,
        "Irritabilidade": irritabilidade,
        "Bateria":        bateria,
        "Sono":           sono,
        "Nevoa":          nevoa,
        "Pressao":        pressao,
        "remedios":       remedios_input if atualizar_rem else remedios_salvos
    }
    try:
        salvar_registro(dados)
        st.balloons()
        st.success("✅ Registro salvo com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

# ─── RELATÓRIO ────────────────────────────────────────────────
st.markdown("---")
st.subheader("📊 Relatório e Análise de Padrões")

if st.button("📈 Gerar Relatório dos Últimos 7 Dias"):
    df_todos = ler_dados()

    if df_todos.empty or "codigo_usuario" not in df_todos.columns:
        st.warning("Ainda não há dados na planilha.")
        st.stop()

    df_user = df_todos[df_todos["codigo_usuario"] == codigo_usuario].copy()
    if df_user.empty:
        st.markdown("""<div style="background:#fff0f0;border:2px solid #ff4444;
        border-radius:12px;padding:20px"><h3 style="color:#cc0000">⚠️ Sem registros</h3>
        <p>Você ainda não fez nenhum registro. Comece hoje!</p></div>""",
        unsafe_allow_html=True)
        st.stop()

    df_user["data"] = pd.to_datetime(df_user["data"])
    df_user = df_user.sort_values("data")
    limite   = pd.to_datetime(date.today() - timedelta(days=7))
    df_7dias = df_user[df_user["data"] >= limite].copy()

    if df_7dias.empty:
        st.markdown("""<div style="background:#fff0f0;border:2px solid #ff4444;
        border-radius:12px;padding:20px"><h3 style="color:#cc0000">⚠️ Sem participação esta semana</h3>
        <p>Nenhum registro nos últimos 7 dias.</p></div>""", unsafe_allow_html=True)
        st.stop()

    # 1. RISCO DE BURNOUT
    st.markdown("### 🔥 Risco de Burnout")
    risco, nivel_risco = calcular_risco_burnout(df_7dias)
    cor_barra = "#4CAF50" if risco < 40 else ("#FF9800" if risco < 70 else "#F44336")

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risco,
        title={"text": f"Nível de Risco — {nivel_risco}", "font": {"size": 18, "color": "#333"}},
        number={"suffix": "%", "font": {"size": 36, "color": "#333"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#333"},
            "bar":  {"color": cor_barra},
            "steps": [
                {"range": [0,  40], "color": "#e8f5e9"},
                {"range": [40, 70], "color": "#fff8e1"},
                {"range": [70,100], "color": "#ffebee"},
            ],
        }
    ))
    fig_gauge.update_layout(paper_bgcolor="#f8f9fa", font=dict(color="#333"),
                            height=280, margin=dict(l=30,r=30,t=60,b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # 2. CARDS DE MÉDIAS
    st.markdown("### 📋 Resumo da Semana")
    cols = st.columns(len(METRICAS))
    for i, m in enumerate(METRICAS):
        if m in df_7dias.columns:
            media = df_7dias[m].mean()
            delta = (df_7dias[m].iloc[-1] - df_7dias[m].iloc[0]
                     if len(df_7dias) > 1 else 0)
            cols[i].metric(label=f"{EMOJIS[m]} {m}",
                           value=f"{media:.1f} / 5",
                           delta=f"{delta:+.0f} vs início")

    # 3. GRÁFICO DE LINHAS + TENDÊNCIA
    st.markdown("### 📈 Evolução com Linha de Tendência")
    fig = go.Figure()
    for metrica in METRICAS:
        if metrica not in df_7dias.columns:
            continue
        fig.add_trace(go.Scatter(
            x=df_7dias["data"], y=df_7dias[metrica],
            mode="lines+markers", name=metrica,
            line=dict(color=CORES_METRICAS[metrica], width=2),
            marker=dict(size=7), opacity=0.9
        ))
        if len(df_7dias) >= 3:
            x_num = np.arange(len(df_7dias))
            y_val = df_7dias[metrica].values.astype(float)
            try:
                z = np.polyfit(x_num, y_val, 1)
                p = np.poly1d(z)
                sinal = "↑ subindo" if z[0] > 0.1 else ("↓ caindo" if z[0] < -0.1 else "→ estável")
                fig.add_trace(go.Scatter(
                    x=df_7dias["data"], y=p(x_num),
                    mode="lines",
                    name=f"Tendência {metrica} ({sinal})",
                    line=dict(color=CORES_METRICAS[metrica], width=1, dash="dot"),
                    opacity=0.45
                ))
            except:
                pass
    fig.update_layout(
        plot_bgcolor="#ffffff", paper_bgcolor="#f8f9fa",
        font=dict(color="#333"),
        legend=dict(bgcolor="#ffffff", bordercolor="#e0e0e0"),
        xaxis=dict(gridcolor="#e0e0e0", title="Data"),
        yaxis=dict(gridcolor="#e0e0e0", range=[0,6], tickmode="linear", dtick=1, title="Nível (1-5)"),
        hovermode="x unified", margin=dict(l=20,r=20,t=40,b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 4. RADAR
    st.markdown("### 🎯 Perfil Geral da Semana")
    labels = [m for m in METRICAS if m in df_7dias.columns]
    medias = [df_7dias[m].mean() for m in labels]
    fig_radar = go.Figure(go.Scatterpolar(
        r=medias + [medias[0]], theta=labels + [labels[0]],
        fill="toself", fillcolor="rgba(33,150,243,0.15)",
        line=dict(color="#2196F3", width=2), marker=dict(size=6)
    ))
    fig_radar.update_layout(
        polar=dict(bgcolor="#ffffff",
            radialaxis=dict(visible=True, range=[0,5], gridcolor="#e0e0e0", color="#555"),
            angularaxis=dict(gridcolor="#e0e0e0", color="#333")),
        paper_bgcolor="#f8f9fa", font=dict(color="#333"),
        margin=dict(l=40,r=40,t=40,b=40)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # 5. MAPA DE CORRELAÇÕES
    st.markdown("### 🔗 Mapa de Correlações entre Indicadores")
    metricas_ex = [m for m in METRICAS if m in df_7dias.columns]
    if len(df_7dias) >= 4:
        corr_matrix = df_7dias[metricas_ex].corr().round(2)
        fig_corr = px.imshow(corr_matrix, text_auto=True,
                             color_continuous_scale="RdBu", zmin=-1, zmax=1,
                             title="Quanto cada indicador influencia o outro")
        fig_corr.update_layout(paper_bgcolor="#f8f9fa", font=dict(color="#333"),
                               margin=dict(l=20,r=20,t=60,b=20))
        st.plotly_chart(fig_corr, use_container_width=True)
        st.caption("💡 +1 = sobem juntos | -1 = um sobe quando o outro cai | 0 = sem relação")
    else:
        st.info("Necessário pelo menos 4 registros para correlações.")

    # 6. COMPARAÇÃO ENTRE SEMANAS
    st.markdown("### 📆 Comparação entre Semanas")
    resumo_semanas = comparar_semanas(df_user)
    if resumo_semanas is not None and len(resumo_semanas) > 1:
        fig_semanas = go.Figure()
        for metrica in METRICAS:
            if metrica in resumo_semanas.columns:
                fig_semanas.add_trace(go.Scatter(
                    x=resumo_semanas["semana"],
                    y=resumo_semanas[metrica],
                    mode="lines+markers",
                    name=metrica,
                    line=dict(color=CORES_METRICAS[metrica], width=2),
                    marker=dict(size=8)
                ))
        fig_semanas.update_layout(
            title="Média de cada indicador por semana — evolução ao longo do tempo",
            plot_bgcolor="#ffffff", paper_bgcolor="#f8f9fa",
            font=dict(color="#333"),
            xaxis=dict(title="Semana", gridcolor="#e0e0e0"),
            yaxis=dict(title="Média (1-5)", range=[0,6],
                       tickmode="linear", dtick=1, gridcolor="#e0e0e0"),
            hovermode="x unified", margin=dict(l=20,r=20,t=60,b=20)
        )
        st.plotly_chart(fig_semanas, use_container_width=True)
        st.markdown("**Médias por semana:**")
        st.dataframe(resumo_semanas.set_index("semana"), use_container_width=True)
    else:
        st.info("📆 Com mais semanas de dados, aparecerá aqui um gráfico comparando a evolução semana a semana.")

    # 7. PADRÕES SEMANAIS
    st.markdown("### 📅 Padrões por Dia da Semana")
    padroes = detectar_padroes_semanais(df_user)
    if padroes:
        for p in padroes:
            st.markdown(f"- {p}")
    else:
        st.info("Necessário pelo menos 7 registros para detectar padrões por dia.")

    # 8. INSIGHTS
    st.markdown("### 💡 Insights Detectados")
    insights = calcular_correlacoes(df_7dias)
    if insights:
        for ins in insights:
            st.markdown(f"- {ins}")
    else:
        st.info("Necessário pelo menos 5 registros para detectar correlações.")

    # 9. PARTICIPAÇÃO
    registros = len(df_7dias)
    if registros < 7:
        st.warning(f"📅 Você registrou {registros} de 7 dias esta semana.")
    else:
        st.success("🎉 Semana completa! Todos os 7 dias registrados.")

    # 10. ALERTA FINAL
    if risco >= 70:
        st.markdown(f"""
        <div style="background:#fff0f0;border:2px solid #F44336;
                    border-radius:12px;padding:20px;margin-top:15px">
            <h3 style="color:#cc0000;margin-top:0">🔴 ALTO RISCO — Ação Recomendada</h3>
            <p style="color:#444">O paciente <b>{nome_usuario}</b> apresenta risco de burnout
            de <b>{risco}%</b>. Recomenda-se revisão urgente.</p>
        </div>""", unsafe_allow_html=True)
    elif risco >= 40:
        st.markdown(f"""
        <div style="background:#fffbe6;border:2px solid #FF9800;
                    border-radius:12px;padding:20px;margin-top:15px">
            <h3 style="color:#e65100;margin-top:0">🟡 ATENÇÃO — Monitorar de Perto</h3>
            <p style="color:#444">O paciente <b>{nome_usuario}</b> apresenta risco moderado
            de <b>{risco}%</b>. Atenção redobrada esta semana.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.success(f"🟢 Risco baixo ({risco}%) — Nenhum sinal crítico esta semana. Continue assim!")
```

E o `requirements.txt` atualizado:
```
streamlit
st-gsheets-connection
pandas
plotly
numpy
    else:
        st.success("✅ Nenhum sinal de alerta detectado esta semana. Continue assim!")
