import streamlit as st
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

# Configuração da página para tela cheia
st.set_page_config(page_title="Painel de Escolha Profissional - 2025", layout="wide")
# Estabelecer conexão com o banco de dados MySQL
# Carregar os dados do CSV em vez de conectar ao banco
@st.cache_data
def load_data():
    return pd.read_csv("dados_salarios_curitiba.csv")  # Substitua pelo caminho correto do seu arquivo

df = load_data()

# Função para classificar nível do cargo
def classificar_nivel(cargo):
    cargo = cargo.lower()
    if any(word in cargo for word in ['junior', 'jr', 'trainee', 'estágio', 'estagio', 'assistente']):
        return 'Junior'
    elif any(word in cargo for word in ['pleno', 'pl']):
        return 'Pleno'
    elif any(word in cargo for word in ['senior', 'sr', 'especialista', 'expert']):
        return 'Senior'
    elif any(word in cargo for word in ['coordenador', 'supervisor', 'líder', 'lider']):
        return 'Coordenação'
    elif any(word in cargo for word in ['gerente', 'gestor']):
        return 'Gerência'
    elif any(word in cargo for word in ['diretor', 'head']):
        return 'Diretoria'
    else:
        return 'Outros'

# Adicionar coluna de nível
df['nivel'] = df['cargo'].apply(classificar_nivel)

# Ordem dos níveis para os gráficos
ordem_niveis = ['Junior', 'Pleno', 'Senior', 'Coordenação', 'Gerência', 'Diretoria', 'Outros']

# Título do Dashboard
st.title("Painel de Escolha Profissional - 2025")

# Criar tabs para separar visão geral e detalhada
tab1, tab2 = st.tabs(["Visão Geral", "Análise Detalhada"])

with tab1:
    st.header("Visão Geral do Mercado")
    
    # 1. Análise por Setor
    st.subheader("Análise por Setor")
    sector_analysis = df.groupby("setor")["salario"].mean().reset_index()
    fig1 = px.bar(sector_analysis, x="setor", y="salario",
                  title="Média Salarial por Setor",
                  labels={"setor": "Setor", "salario": "Salário Médio (R$)"})
    fig1.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig1, use_container_width=True)

    # 2. Análise por Setor e Área
    st.subheader("Análise por Setor e Área")
    sector_area_analysis = df.groupby(["setor", "area"])["salario"].mean().reset_index()
    fig2 = px.bar(sector_area_analysis, x="setor", y="salario", color="area",
                  title="Média Salarial por Setor e Área",
                  labels={"setor": "Setor", "salario": "Salário Médio (R$)", "area": "Área"})
    fig2.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig2, use_container_width=True)

    # 3. Análise por Especialidade por Setor
    st.subheader("Análise por Especialidade por Setor")
    specialization_sector_analysis = df.groupby(["especialidade", "setor"])["salario"].mean().reset_index()
    fig3 = px.bar(specialization_sector_analysis, x="especialidade", y="salario", color="setor",
                  title="Média Salarial por Especialidade e Setor",
                  labels={"especialidade": "Especialidade", "salario": "Salário Médio (R$)", "setor": "Setor"})
    fig3.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig3, use_container_width=True)

    # 4. Top 10 Salários Médios por Área
    st.subheader("Top 10 Áreas com Maiores Salários Médios")
    top_areas = df.groupby("area")["salario"].mean().sort_values(ascending=False).head(10).reset_index()
    fig4 = px.bar(top_areas, x="area", y="salario",
                  title="Top 10 Áreas - Salário Médio",
                  labels={"area": "Área", "salario": "Salário Médio (R$)"})
    fig4.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig4, use_container_width=True)

    # 5. Distribuição de Profissões em Alta por Setor
    st.subheader("Setores com Profissões em Alta")
    em_alta = df[df["em_alta"].notna()]
    em_alta_setor = em_alta.groupby("setor")["cargo"].agg(list).reset_index()
    em_alta_setor["cargo"] = em_alta_setor["cargo"].apply(lambda x: ', '.join(x))
    
    fig5 = px.pie(em_alta_setor, values=em_alta_setor["cargo"].apply(len), names="setor",
                  title="Distribuição de Profissões em Alta por Setor",
                  hover_data=["cargo"],
                  labels={"cargo": "Cargos"})
    fig5.update_traces(hovertemplate='<b>%{label}</b><br>Cargos: %{customdata}')
    st.plotly_chart(fig5, use_container_width=True)

    # 6. Comparativo de Salários por Porte de Empresa
    st.subheader("Salários por Porte de Empresa")
    salary_by_size = df.groupby("empresa")["salario"].agg(["mean", "min", "max"]).reset_index()
    salary_by_size.columns = ["Porte da Empresa", "Média", "Mínimo", "Máximo"]
    st.write("""
    **Legenda - Porte das Empresas:**
    - pq: Pequeno Porte
    - md: Médio Porte
    - gr: Grande Porte
    """)
    st.table(salary_by_size.round(2))

with tab2:
    st.header("Análise Detalhada")
    
    # Filtros para análise detalhada
    col1, col2 = st.columns(2)
    with col1:
        escolha_setor = st.selectbox("Escolha um setor", ["Todos"] + list(df["setor"].dropna().unique()))
        escolha_area = st.selectbox("Escolha uma área", ["Todas"] + list(df["area"].dropna().unique()))
    
    with col2:
        escolha_regiao = st.selectbox("Escolha uma região", ["Todas"] + list(df["regiao"].dropna().unique()))
        escolha_empresa = st.selectbox("Porte da empresa", ["Todas"] + list(df["empresa"].dropna().unique()))

    # Aplicar filtros
    filtered_df = df.copy()
    if escolha_setor != "Todos":
        filtered_df = filtered_df[filtered_df["setor"] == escolha_setor]
    if escolha_area != "Todas":
        filtered_df = filtered_df[filtered_df["area"] == escolha_area]
    if escolha_regiao != "Todas":
        filtered_df = filtered_df[filtered_df["regiao"] == escolha_regiao]
    if escolha_empresa != "Todas":
        filtered_df = filtered_df[filtered_df["empresa"] == escolha_empresa]

    # 1. Tabela de Cargos e Salários
    st.subheader("Cargos e Salários")
    cargo_stats = filtered_df.groupby("cargo").agg({
        "salario": ["mean", "min", "max"],
        "em_alta": lambda x: "Sim" if x.notna().any() else "Não",
        "setor": "first",
        "area": "first",
        "nivel": "first"
    }).reset_index()
    cargo_stats.columns = ["Cargo", "Média Salarial", "Salário Mínimo", "Salário Máximo", "Em Alta", "Setor", "Área", "Nível"]
    st.dataframe(cargo_stats.sort_values("Média Salarial", ascending=False).round(2))

    # 2. Gráfico de Distribuição Salarial
    st.subheader("Distribuição Salarial dos Cargos")
    
    # Opção de visualização
    tipo_visualizacao = st.radio(
        "Escolha o tipo de visualização:",
        ["Por Cargo", "Por Nível de Carreira"],
        horizontal=True
    )
    
    if tipo_visualizacao == "Por Cargo":
        # Filtrar cargos com dados
        cargos_disponiveis = filtered_df["cargo"].unique()
        cargo_selecionado = st.selectbox("Escolha um cargo:", ["Todos"] + list(cargos_disponiveis))
        
        if cargo_selecionado != "Todos":
            dados_plot = filtered_df[filtered_df["cargo"] == cargo_selecionado]
        else:
            dados_plot = filtered_df
            
        fig6 = px.box(dados_plot, x="cargo", y="salario", 
                      color="empresa",
                      title="Distribuição Salarial por Cargo e Porte da Empresa",
                      labels={"cargo": "Cargo", "salario": "Salário (R$)", "empresa": "Porte da Empresa"})
    else:
        # Usar a classificação por nível
        nivel_selecionado = st.selectbox("Escolha um nível:", ["Todos"] + ordem_niveis)
        
        if nivel_selecionado != "Todos":
            dados_plot = filtered_df[filtered_df["nivel"] == nivel_selecionado]
        else:
            dados_plot = filtered_df
            
        fig6 = px.box(dados_plot, x="nivel", y="salario", 
                      color="empresa",
                      category_orders={"nivel": ordem_niveis},
                      title="Distribuição Salarial por Nível e Porte da Empresa",
                      labels={"nivel": "Nível", "salario": "Salário (R$)", "empresa": "Porte da Empresa"})
    
    fig6.update_layout(xaxis_tickangle=-45, height=600)
    st.plotly_chart(fig6, use_container_width=True)

    # 3. Gráfico de Progressão de Carreira
    st.subheader("Progressão de Carreira")
    nivel_filtered = filtered_df.groupby('nivel')['salario'].agg(['mean', 'min', 'max']).reset_index()
    nivel_filtered['nivel'] = pd.Categorical(nivel_filtered['nivel'], categories=ordem_niveis, ordered=True)
    nivel_filtered = nivel_filtered.sort_values('nivel')
    
    fig_progression_filtered = go.Figure()
    fig_progression_filtered.add_trace(go.Scatter(x=nivel_filtered['nivel'], y=nivel_filtered['mean'],
                                                mode='lines+markers', name='Média',
                                                line=dict(color='blue', width=2)))
    fig_progression_filtered.add_trace(go.Scatter(x=nivel_filtered['nivel'], y=nivel_filtered['min'],
                                                mode='lines', name='Mínimo',
                                                line=dict(color='red', dash='dash')))
    fig_progression_filtered.add_trace(go.Scatter(x=nivel_filtered['nivel'], y=nivel_filtered['max'],
                                                mode='lines', name='Máximo',
                                                line=dict(color='green', dash='dash')))
    
    fig_progression_filtered.update_layout(
        title="Progressão Salarial por Nível",
        xaxis_title="Nível",
        yaxis_title="Salário (R$)",
        height=400
    )
    st.plotly_chart(fig_progression_filtered, use_container_width=True)

    # 4. Análise Regional (se houver dados de região)
    if escolha_regiao == "Todas" and filtered_df["regiao"].notna().any():
        st.subheader("Análise Regional")
        regional_avg = filtered_df.groupby("regiao")["salario"].mean().reset_index()
        fig7 = px.bar(regional_avg, x="regiao", y="salario",
                      title="Média Salarial por Região",
                      labels={"regiao": "Região", "salario": "Salário Médio (R$)"})
        st.plotly_chart(fig7, use_container_width=True)

    # 5. Especialidades (se houver)
    if filtered_df["especialidade"].notna().any():
        st.subheader("Análise por Especialidade")
        spec_avg = filtered_df.groupby("especialidade")["salario"].mean().sort_values(ascending=False).reset_index()
        fig8 = px.bar(spec_avg, x="especialidade", y="salario",
                      title="Média Salarial por Especialidade",
                      labels={"especialidade": "Especialidade", "salario": "Salário Médio (R$)"})
        fig8.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig8, use_container_width=True)

    # Insights baseados nos filtros selecionados
    st.subheader("📊 Insights")
    
    # Calcular estatísticas relevantes
    media_geral = filtered_df["salario"].mean()
    cargos_em_alta = filtered_df[filtered_df["em_alta"].notna()][["cargo", "setor", "area", "empresa", "salario", "nivel"]]
    
    st.write(f"""
    **Análise dos Dados Filtrados:**
    - Média Salarial: R$ {media_geral:,.2f}
    - Número de Cargos Diferentes: {filtered_df["cargo"].nunique()}
    - Cargos em Alta: {len(cargos_em_alta)}
    """)

    if len(cargos_em_alta) > 0:
        st.subheader("Cargos em Alta Demanda")
        st.dataframe(cargos_em_alta.rename(columns={
            "cargo": "Cargo",
            "setor": "Setor",
            "area": "Área",
            "empresa": "Porte da Empresa",
            "salario": "Salário Médio",
            "nivel": "Nível"
        }).round(2))
