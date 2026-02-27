import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Meu Diário de Saúde Mental", page_icon="🧠")

st.title("🧠 Diário de Monitoramento Psicológico")

# Nome do arquivo onde vamos salvar
ARQUIVO_DADOS = "dados.csv"

# Interface
with st.form("diario_form"):
    st.subheader("Como você se sente hoje?")
    
    humor = st.select_slider("Valência do Humor", options=[1, 2, 3, 4, 5], value=3)
    irritabilidade = st.select_slider("Irritabilidade", options=[1, 2, 3, 4, 5], value=1)
    bateria = st.select_slider("Bateria Social", options=[1, 2, 3, 4, 5], value=3)
    sono = st.select_slider("Qualidade do Sono", options=[1, 2, 3, 4, 5], value=3)
    nevoa = st.select_slider("Clareza Mental", options=[1, 2, 3, 4, 5], value=3)
    pressao = st.select_slider("Sentimento de Pressão", options=[1, 2, 3, 4, 5], value=1)

    submit = st.form_submit_button("💾 Salvar Registro de Hoje")

if submit:
    # Criar a linha com os dados
    novo_registro = f"\n{date.today()},{humor},{irritabilidade},{bateria},{sono},{nevoa},{pressao}"
    
    # Salvar direto no arquivo CSV
    with open(ARQUIVO_DADOS, "a") as f:
        f.write(novo_registro)
    
    st.balloons()
    st.success("Dados salvos com sucesso!")

# Mostrar o histórico
st.markdown("---")
if st.checkbox("Ver histórico de registros"):
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
        st.dataframe(df)
