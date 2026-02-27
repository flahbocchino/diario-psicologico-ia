🧠 Monitor de Saúde Mental com IA

Sistema de monitoramento psicológico inteligente, desenvolvido para auxiliar profissionais de saúde mental no acompanhamento de pacientes ao longo do tempo.
🔗 Acessar o sistema - https://diario-psicologico-ia-zh4xsx2kgk3qcpnxniqcrg.streamlit.app/
📌 Sobre o Projeto
Este projeto nasceu de uma necessidade real: criar uma ferramenta simples, acessível e segura para que pacientes possam registrar seu estado emocional e psicológico diariamente, e que esses dados sejam transformados em relatórios úteis para o profissional de saúde responsável.
O sistema foi construído do zero como projeto de portfólio, com foco em psicologia, análise de dados e desenvolvimento web, sem necessidade de instalação — tudo roda no navegador.

✨ Funcionalidades

🔐 Login com nome fictício e senha — o paciente pode manter sua privacidade total
💊 Registro de medicamentos — nome, dosagem e horário, atualizável a qualquer momento
📝 Questionário diário rápido — 6 indicadores em escala de 1 a 5, feito para ser respondido em menos de 1 minuto
📊 Relatório semanal automático com:

Barra de risco de burnout (0% a 100%)
Cards com médias de cada indicador
Gráfico de evolução com linha de tendência
Gráfico radar do perfil geral da semana
Mapa de calor de correlações entre indicadores
Comparação entre semanas (memória de longo prazo)
Detecção de padrões por dia da semana
Insights automáticos de correlações


⚠️ Alertas automáticos para o profissional de saúde (risco baixo, atenção ou alto risco)
📄 Exportação em PDF — relatório completo e profissional para entregar à psicóloga


📈 Indicadores Monitorados
IndicadorEscalaO que mede😊 Humor1 (Triste) → 5 (Feliz)Valência emocional geral😤 Irritabilidade1 (Calmo) → 5 (Irritado)Limiar de tolerância emocional🔋 Bateria Social1 (Esgotado) → 5 (Sociável)Energia para interações sociais😴 Qualidade do Sono1 (Péssimo) → 5 (Ótimo)Recuperação física e mental🧩 Foco Mental1 (Confuso) → 5 (Claro)Névoa cognitiva e concentração🌡️ Pressão Interna1 (Tranquilo) → 5 (Exausto)Carga percebida de demandas

🔥 Como o Risco de Burnout é Calculado
O sistema utiliza um algoritmo com pesos diferenciados por indicador, baseado em critérios clínicos de esgotamento mental:

Pressão Interna → peso 2.0 (maior impacto)
Humor → peso 2.0
Sono → peso 1.5
Irritabilidade → peso 1.5
Bateria Social → peso 1.0
Névoa Mental → peso 1.0

O resultado é apresentado em porcentagem com três níveis de alerta:

🟢 0–39% — Estável
🟡 40–69% — Atenção
🔴 70–100% — Alto Risco


🧠 Inteligência de Padrões
Com o acúmulo de dados ao longo das semanas, o sistema passa a identificar automaticamente:

Correlações entre indicadores (ex: "quando o sono piora, o humor tende a cair")
Padrões por dia da semana (ex: "toda segunda-feira a pressão é mais alta")
Tendências de melhora ou piora ao longo da semana
Comparação entre semanas — permitindo ver a evolução do paciente ao longo de meses


🛠️ Tecnologias Utilizadas
TecnologiaFunçãoPythonLinguagem principalStreamlitInterface web e hospedagemGoogle SheetsBanco de dados em nuvemPlotlyGráficos interativosReportLabGeração de PDFNumPy / PandasAnálise e manipulação de dadosGoogle Cloud (Service Account)Autenticação segura com a planilhaGitHubVersionamento do código

🔒 Privacidade e Segurança

O paciente pode usar nome fictício no cadastro
A senha gera um código único criptografado (MD5) — nenhuma senha é armazenada diretamente
As credenciais de acesso ao banco de dados ficam protegidas nos Secrets do Streamlit, nunca expostas no código
Os dados ficam armazenados em uma planilha privada no Google Drive
🗂️ Estrutura do Projeto
diario-psicologico-ia/
│
├── streamlit_app.py     # Código principal do sistema
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação (você está aqui)

🚀 Como Rodar Localmente

O sistema foi projetado para rodar 100% online, mas se quiser rodar localmente:

bash# 1. Clone o repositório
git clone https://github.com/flahbocchino/diario-psicologico-ia

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure os Secrets do Streamlit com suas credenciais do Google

# 4. Rode o app
streamlit run streamlit_app.py

📄 Exemplo de Relatório PDF
O sistema gera automaticamente um relatório em PDF ao final de cada semana, contendo:

Identificação do paciente e período analisado
Medicamentos em uso
Nível de risco de burnout
Tabela de médias e tendências por indicador
Registros diários da semana
Correlações e padrões identificados
Recomendação para o profissional de saúde


👩‍💻 Sobre a Desenvolvedora
Projeto desenvolvido por flahbocchino como parte do portfólio de desenvolvimento.
Combinando interesse em saúde mental, análise de dados e desenvolvimento de software, este projeto busca mostrar como a tecnologia pode ser uma aliada no cuidado psicológico.



Este sistema é uma ferramenta de apoio. Os relatórios gerados devem sempre ser interpretados por um profissional de saúde qualificado.
