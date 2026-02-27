import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# Configuração da página para ficar bonita no PC
st.set_page_config(page_title="Meu Diário de Saúde Mental", page_icon="🧠", layout="centered")

st.title("🧠 Diário de Monitoramento Psicológico")
st.markdown("---")

# --- CONEXÃO COM O GOOGLE SHEETS ---
# Usando o link que você me enviou
url = "https://docs.google.com/spreadsheets/d/1vSR4W34p1g80bie4CjRdyzm1_OJliRpA0VUtnNz1D_g/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FORMULÁRIO DE ENTRADA ---
with st.form("diario_form"):
    st.subheader("Como você se sente hoje?")
    st.info("Arraste os seletores abaixo (1 é o nível mais baixo e 5 o mais alto).")
    
    humor = st.select_slider("Valência do Humor (Triste -> Radiante)", options=[1, 2, 3, 4, 5], value=3)
    irritabilidade = st.select_slider("Nível de Irritabilidade (Paciente -> Irritado)", options=[1, 2, 3, 4, 5], value=1)
    bateria = st.select_slider("Bateria Social (Isolado -> Sociável)", options=[1, 2, 3, 4, 5], value=3)
    sono = st.select_slider("Qualidade do Sono (Moído -> Renovado)", options=[1, 2, 3, 4, 5], value=3)
    nevoa = st.select_slider("Clareza Mental (Confuso -> Focado)", options=[1, 2, 3, 4, 5], value=3)
    pressao = st.select_slider("Sentimento de Pressão (Sob controle -> Exausto)", options=[1, 2, 3, 4, 5], value=1)

    st.markdown("---")
    submit = st.form_submit_button("💾 Salvar Registro de Hoje")

if submit:
    # Preparando os dados para salvar
    novo_registro = pd.DataFrame([{
        "data": str(date.today()),
        "Humor": humor,
        "Irritabilidade": irritabilidade,
        "Bateria": bateria,
        "Sono": sono,
        "Nevoa": nevoa,
        "Pressao": pressao
    }])
    
    try:
        # Tenta ler a planilha existente
        dados_antigos = conn.read(spreadsheet=url)
        # Junta o novo registro aos antigos
        dados_atualizados = pd.concat([dados_antigos, novo_registro], ignore_index=True)
        # Atualiza a planilha no Google Drive
        conn.update(spreadsheet=url, data=dados_atualizados)
        
        st.balloons()
        st.success("Dados enviados para a planilha com sucesso!")
        st.write("Verifique sua planilha agora: os dados devem aparecer lá em segundos.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao salvar. Verifique se a planilha está como 'Editor' para qualquer pessoa com o link. Erro: {e}")

# --- VISUALIZAÇÃO DOS DADOS (OPCIONAL PARA TESTE) ---
if st.checkbox("Mostrar histórico salvo na planilha"):
    historico = conn.read(spreadsheet=url)
    st.dataframe(historico)
