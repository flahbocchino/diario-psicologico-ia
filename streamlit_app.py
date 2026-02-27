import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Meu Diário de Saúde Mental", page_icon="🧠")

st.title("🧠 Diário de Monitoramento Psicológico")
st.write("Registre como você está hoje. No final de 7 dias, geraremos seu relatório.")

# Criando o formulário de "cliques"
with st.form("diario_form"):
    st.subheader("Como você se sente hoje?")
    
    humor = st.select_slider("Valência do Humor (Triste -> Radiante)", options=[1, 2, 3, 4, 5], value=3)
    irritabilidade = st.select_slider("Nível de Irritabilidade (Paciente -> Irritado)", options=[1, 2, 3, 4, 5], value=1)
    bateria = st.select_slider("Bateria Social (Isolado -> Sociável)", options=[1, 2, 3, 4, 5], value=3)
    sono = st.select_slider("Qualidade do Sono (Moído -> Renovado)", options=[1, 2, 3, 4, 5], value=3)
    nevoa = st.select_slider("Clareza Mental (Confuso -> Focado)", options=[1, 2, 3, 4, 5], value=3)
    pressao = st.select_slider("Sentimento de Pressão (Sob controle -> Exausto)", options=[1, 2, 3, 4, 5], value=1)

    submit = st.form_submit_button("Salvar Registro de Hoje")

if submit:
    st.success(f"Registro de {date.today()} salvo com sucesso! (Simulação)")
    # No próximo passo, vamos criar o banco de dados para salvar de verdade
