import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, timedelta
import plotly.express as px

st.set_page_config(page_title="Monitor de Saúde Mental", layout="wide")

# URL da sua planilha (que você já configurou como Editor)
url = "https://docs.google.com/spreadsheets/d/1vSR4W34p1g80bie4CjRdyzm1_OJliRpA0VUtnNz1D_g/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🧠 Diário Psicológico Inteligente")

# 1. IDENTIFICAÇÃO (Cadastro/Login)
nome_usuario = st.text_input("Digite seu nome ou apelido fictício para login:", placeholder="Ex: Usuário01")

if nome_usuario:
    st.sidebar.success(f"Logado como: {nome_usuario}")
    
    # 2. MEDICAMENTOS
    st.subheader("💊 Gestão de Medicamentos")
    remedios_input = st.text_area("Liste os remédios que você toma (Nome, Dosagem, Horário):", 
                                  placeholder="Ex: Sertralina 50mg - 08:00")

    # 3. QUESTIONÁRIO DIÁRIO
    st.markdown("---")
    st.subheader("📝 Como você está hoje?")
    
    with st.form("diario_form"):
        c1, c2 = st.columns(2)
        with c1:
            humor = st.select_slider("Humor (Triste -> Feliz)", options=[1,2,3,4,5], value=3)
            irritabilidade = st.select_slider("Irritabilidade (Calmo -> Irritado)", options=[1,2,3,4,5], value=1)
            bateria = st.select_slider("Bateria Social (Esgotado -> Sociável)", options=[1,2,3,4,5], value=3)
        with c2:
            sono = st.select_slider("Qualidade do Sono (Péssimo -> Ótimo)", options=[1,2,3,4,5], value=3)
            nevoa = st.select_slider("Foco/Névoa Mental (Confuso -> Claro)", options=[1,2,3,4,5], value=3)
            pressao = st.select_slider("Sentimento de Pressão (Tranquilo -> Exausto)", options=[1,2,3,4,5], value=1)
        
        st.info("Você alterou ou quer atualizar seus remédios hoje?")
        atualizar_rem = st.checkbox("Sim, atualizar dados de medicação")
        
        submit = st.form_submit_button("Salvar Registro Diário")

    if submit:
        # Preparar dados para salvar
        novo_registro = pd.DataFrame([{
            "data": str(date.today()),
            "Humor": humor,
            "Irritabilidade": irritabilidade,
            "Bateria": bateria,
            "Sono": sono,
            "Nevoa": nevoa,
            "Pressao": pressao,
            "nome": nome_usuario,
            "remedios": remedios_input
        }])
        
        try:
            # Tenta ler dados existentes para não apagar o que já tem
            try:
                df_atual = conn.read(spreadsheet=url)
            except:
                df_atual = pd.DataFrame()
                
            df_final = pd.concat([df_atual, novo_registro], ignore_index=True)
            conn.update(spreadsheet=url, data=df_final)
            st.balloons()
            st.success("✅ Registro salvo com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

    # 4. RELATÓRIOS E ALERTAS (Lógica de 7 dias)
    st.markdown("---")
    st.subheader("📊 Análise de Padrões e Relatórios")
    
    if st.button("Gerar Relatório de 7 Dias"):
        try:
            df_completo = conn.read(spreadsheet=url)
            # Filtra apenas os dados do usuário atual
            df_user = df_completo[df_completo['nome'] == nome_usuario].copy()
            
            if df_user.empty:
                st.warning("Você ainda não possui registros cadastrados.")
            else:
                df_user['data'] = pd.to_datetime(df_user['data'])
                uma_semana_atras = pd.to_datetime(date.today() - timedelta(days=7))
                df_7dias = df_user[df_user['data'] >= uma_semana_atras]

                if df_7dias.empty:
                    st.markdown("<div style='background-color: #ffcccc; padding: 15px; border-radius: 5px; color: #990000; text-align: center;'><b>⚠️ AVISO:</b> Você não participou nos últimos 7 dias.</div>", unsafe_allow_html=True)
                else:
                    fig = px.line(df_7dias, x="data", y=["Humor", "Sono", "Pressao"], 
                                  title="Sua Evolução na Semana", markers=True)
                    st.plotly_chart(fig, use_container_width=True)

                    # ALERTA AMARELO PARA O PROFISSIONAL
                    if len(df_7dias) >= 3:
                        media_pressao = df_7dias['Pressao'].tail(3).mean()
                        if media_pressao >= 4:
                            st.markdown("""
                            <div style="background-color: #ffffcc; padding: 20px; border: 2px solid #ffcc00; border-radius: 10px;">
                                <h3 style="color: #665500; margin-top: 0;">⚠️ ALERTA AO PROFISSIONAL</h3>
                                <p>Padrão de <b>esgotamento/burnout</b> detectado. Recomenda-se revisão imediata.</p>
                            </div>
                            """, unsafe_allow_html=True)
        except:
            st.info("Ainda não há dados na planilha para analisar.")

else:
    st.info("Por favor, digite seu nome no campo acima para acessar o sistema.")
