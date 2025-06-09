import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from sklearn.preprocessing import StandardScaler

# --- Configuração da Página ---
st.set_page_config(page_title="📊 Dashboard Mobile BI", layout="wide")
st.markdown("## 📱 Dashboard de Uso de Dispositivos Móveis e Comportamento de Usuários")
st.markdown("---")

# --- Carregamento dos Dados (com cache para performance) ---
@st.cache_data
def load_data():
    df = pd.read_csv("user_behavior_dataset.csv")

    
    # pré - processamento
    num_cols = df.select_dtypes(include='number').columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].mean())

    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    df[cat_cols] = df[cat_cols].fillna(df[cat_cols].mode().iloc[0])


    return df

df = load_data()

# --- Validação das Colunas ---
required_columns = [
    "Operating System", "Gender", "User Behavior Class", "Device Model",
    "App Usage Time (min/day)", "Screen On Time (hours/day)",
    "Battery Drain (mAh/day)", "Number of Apps Installed",
    "Data Usage (MB/day)", "Age"
]
missing_cols = [col for col in required_columns if col not in df.columns]
if missing_cols:
    st.error(f"Erro Crítico: As seguintes colunas obrigatórias estão ausentes no seu arquivo CSV: {', '.join(missing_cols)}")
    st.stop()

# --- Barra Lateral de Filtros ---
st.sidebar.header("🎛️ Filtros Interativos")

# Filtros Categóricos
os_options = st.sidebar.multiselect("Sistema Operacional", df["Operating System"].unique(), default=df["Operating System"].unique())
gender_options = st.sidebar.multiselect("Gênero", df["Gender"].unique(), default=df["Gender"].unique())
class_options = st.sidebar.multiselect("Classe Comportamental", sorted(df["User Behavior Class"].unique()), default=sorted(df["User Behavior Class"].unique()))
model_options = st.sidebar.multiselect("Modelo de Dispositivo", df["Device Model"].unique(), default=df["Device Model"].unique())

# Filtros Numéricos (Sliders)
st.sidebar.subheader("📉 Intervalos Numéricos")
def create_slider(column_name, label):
    min_val = float(df[column_name].min())
    max_val = float(df[column_name].max())
    return st.sidebar.slider(label, min_val, max_val, (min_val, max_val))

usage_range = create_slider("App Usage Time (min/day)", "Uso de App (min/dia)")
screen_range = create_slider("Screen On Time (hours/day)", "Tela Ativa (h/dia)")
batt_range = create_slider("Battery Drain (mAh/day)", "Drenagem de Bateria (mAh)")
apps_range = create_slider("Number of Apps Installed", "Número de Apps Instalados")
data_range = create_slider("Data Usage (MB/day)", "Uso de Dados (MB)")
age_range = create_slider("Age", "Idade")


# --- Aplicação dos Filtros no DataFrame ---
filtered_df = df[
    df["Operating System"].isin(os_options) &
    df["Gender"].isin(gender_options) &
    df["User Behavior Class"].isin(class_options) &
    df["Device Model"].isin(model_options) &
    df["App Usage Time (min/day)"].between(*usage_range) &
    df["Screen On Time (hours/day)"].between(*screen_range) &
    df["Battery Drain (mAh/day)"].between(*batt_range) &
    df["Number of Apps Installed"].between(*apps_range) &
    df["Data Usage (MB/day)"].between(*data_range) &
    df["Age"].between(*age_range)
]

# Mensagem de aviso se nenhum dado corresponder aos filtros
if filtered_df.empty:
    st.warning("Nenhum dado encontrado com os filtros aplicados. Por favor, ajuste os filtros.")
    st.stop()

# --- KPIs Principais (Visão Geral) ---
st.markdown("### 📌 Visão Geral da Seleção Atual")
col1, col2, col3, col4 = st.columns(4)
col1.metric("📱 Uso Médio de App", f"{filtered_df['App Usage Time (min/day)'].mean():.1f} min")
col2.metric("🕒 Média de Tela Ativa", f"{filtered_df['Screen On Time (hours/day)'].mean():.1f} h")
col3.metric("🌐 Consumo Médio de Dados", f"{filtered_df['Data Usage (MB/day)'].mean():.1f} MB")
col4.metric("📦 Média de Apps Instalados", f"{filtered_df['Number of Apps Installed'].mean():.1f}")

st.markdown("---")

# --- Seção de Gráficos ---

with st.expander("📊 Distribuições e Proporções", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        fig_os = px.pie(filtered_df, names="Operating System", title="Distribuição por SO", hole=0.3,
                        color_discrete_sequence=px.colors.sequential.Plasma)
        fig_os.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_os, use_container_width=True)
    with c2:
        fig_class = px.pie(filtered_df, names="User Behavior Class", title="Distribuição por Classe Comportamental", hole=0.3,
                           color_discrete_sequence=px.colors.sequential.Viridis)
        fig_class.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_class, use_container_width=True)

# --- INSIGHTS INTELIGENTES E GRÁFICOS AVANÇADOS ---

# 1. Análise Comparativa por Classe
st.markdown("### 🆚 Análise Comparativa por Classe de Comportamento")
col1, col2 = st.columns(2)
class_compare_1 = col1.selectbox("Selecione a primeira classe para comparar:", sorted(df["User Behavior Class"].unique()), index=0)
class_compare_2 = col2.selectbox("Selecione a segunda classe para comparar:", sorted(df["User Behavior Class"].unique()), index=len(df["User Behavior Class"].unique())-1)

compare_df = filtered_df[filtered_df["User Behavior Class"].isin([class_compare_1, class_compare_2])]

if not compare_df.empty:
    metrics_to_compare = ['Data Usage (MB/day)', 'Number of Apps Installed', 'Battery Drain (mAh/day)']
    compare_grouped = compare_df.groupby("User Behavior Class")[metrics_to_compare].mean().reset_index()
    
    fig_compare = px.bar(
        compare_grouped,
        x="User Behavior Class",
        y=metrics_to_compare,
        barmode='group',
        title=f"Comparativo Médio: Classe {class_compare_1} vs. Classe {class_compare_2}",
        labels={"value": "Valor Médio", "User Behavior Class": "Classe de Comportamento"}
    )
    st.plotly_chart(fig_compare, use_container_width=True)
else:
    st.warning(f"Não há dados disponíveis para as classes {class_compare_1} e/ou {class_compare_2} com os filtros atuais.")


# 2. Análise de Comportamento: iOS vs. Android
with st.expander("⚔️ Análise de Comportamento: iOS vs. Android", expanded=False):
    metric_to_compare_os = st.selectbox(
        "Selecione a métrica para comparar entre SO:",
        ['App Usage Time (min/day)', 'Data Usage (MB/day)', 'Number of Apps Installed', 'Battery Drain (mAh/day)'],
        key='os_comparison'
    )
    
    fig_box = px.box(
        filtered_df,
        x="Operating System",
        y=metric_to_compare_os,
        color="Operating System",
        title=f"Distribuição de '{metric_to_compare_os}' por Sistema Operacional",
        color_discrete_map={"Android": "#3DDC84", "iOS": "#A9A9A9"},
        notched=True 
    )
    st.plotly_chart(fig_box, use_container_width=True)

# --- GRÁFICOS SOBRE IDADE SUBSTITUÍDOS ---

# 3. Gráfico de Barras: Média de Uso de Apps por Faixa Etária
with st.expander("⏳ Média de Uso de Apps por Faixa Etária", expanded=True):
    # Criar uma cópia para evitar o SettingWithCopyWarning
    df_age_usage = filtered_df.copy()
    
    # Definir os intervalos e rótulos para as faixas etárias
    age_bins = [df_age_usage['Age'].min() - 1, 20, 30, 40, 50, df_age_usage['Age'].max()]
    age_labels = ['Até 20', '21-30', '31-40', '41-50', 'Acima de 50']
    df_age_usage['Age Group'] = pd.cut(df_age_usage['Age'], bins=age_bins, labels=age_labels, right=True)
    
    # Calcular a média de uso por grupo de idade
    avg_usage_by_age = df_age_usage.groupby('Age Group')['App Usage Time (min/day)'].mean().reset_index()
    
    # Criar o gráfico de barras
    fig_bar_age = px.bar(
        avg_usage_by_age,
        x='Age Group',
        y='App Usage Time (min/day)',
        text_auto='.2s', # Formata o texto para exibir o valor em cima da barra
        title='Média de Tempo de Uso de Apps por Faixa Etária',
        labels={'Age Group': 'Faixa Etária', 'App Usage Time (min/day)': 'Média de Uso (min/dia)'}
    )
    fig_bar_age.update_traces(textposition='outside')
    st.plotly_chart(fig_bar_age, use_container_width=True)

# 4. Gráfico de Barras Empilhadas: Modelos de Celular por Faixa Etária
with st.expander("📱 Modelos de Celular por Faixa Etária", expanded=True):
    # Criar uma cópia para evitar o SettingWithCopyWarning
    df_age_model = filtered_df.copy()
    
    # Reutilizar os mesmos bins e labels da análise anterior
    age_bins = [df_age_model['Age'].min() - 1, 20, 30, 40, 50, df_age_model['Age'].max()]
    age_labels = ['Até 20', '21-30', '31-40', '41-50', 'Acima de 50']
    df_age_model['Age Group'] = pd.cut(df_age_model['Age'], bins=age_bins, labels=age_labels, right=True)

    # Contar a ocorrência de cada modelo por faixa etária
    model_counts_by_age = df_age_model.groupby(['Age Group', 'Device Model']).size().reset_index(name='Count')

    # Criar o gráfico de barras empilhadas
    fig_stacked_bar = px.bar(
        model_counts_by_age,
        x='Age Group',
        y='Count',
        color='Device Model',
        title='Distribuição de Modelos de Celular por Faixa Etária',
        labels={'Age Group': 'Faixa Etária', 'Count': 'Número de Usuários', 'Device Model': 'Modelo do Celular'}
    )
    st.plotly_chart(fig_stacked_bar, use_container_width=True)

# --- FIM DA SUBSTITUIÇÃO ---

# 5. Análise de Correlações
with st.expander("📈 Correlação entre Variáveis Numéricas", expanded=False):
    numeric_cols = ['App Usage Time (min/day)', 'Screen On Time (hours/day)', 'Battery Drain (mAh/day)', 'Number of Apps Installed', 'Data Usage (MB/day)', 'Age']
    corr_matrix = filtered_df[numeric_cols].corr()
    
    fig_heatmap = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                            color_continuous_scale='RdYlBu',
                            title="Mapa de Calor de Correlações")
    st.plotly_chart(fig_heatmap, use_container_width=True)


# 6. Oportunidades de Marketing por Eficiência
with st.expander("🎯 Oportunidades de Marketing por Eficiência", expanded=False):
    fig_scatter = px.scatter(
        filtered_df,
        x="Battery Drain (mAh/day)",
        y="App Usage Time (min/day)",
        color="User Behavior Class",
        size='Data Usage (MB/day)', 
        hover_data=['Device Model', 'Gender', 'Age', 'Operating System'],
        title="Uso de App vs. Consumo de Bateria (Tamanho por Uso de Dados)",
        color_continuous_scale=px.colors.sequential.Inferno
    )
    fig_scatter.update_layout(legend_title_text='Classe de Comportamento')
    st.plotly_chart(fig_scatter, use_container_width=True)


# --- CONTEXTO ANALÍTICO ---
st.markdown("---")
st.markdown("### 🤔 Contexto Analítico: Uma Observação sobre o Período dos Dados")
st.info(
    """
    **Observação Importante:** Os modelos de dispositivos presentes no dataset (ex: Google Pixel 5, iPhone 12, Samsung Galaxy S21) 
    sugerem que os dados podem ter sido coletados por volta de **2021-2022**. Este período coincide com a pandemia de COVID-19, 
    um fator que pode ter intensificado os padrões de uso de dispositivos móveis, potencialmente elevando métricas como 
    tempo de tela e uso de apps em comparação com períodos pré ou pós-pandêmicos.
    """
)


# --- Seção Final de Insights Dinâmicos ---
st.markdown("---")
st.markdown("### 💡 Insights Dinâmicos da Seleção Atual")

# Cálculo dos insights baseado nos dados filtrados
# Insight de Eficiência
filtered_df['Efficiency (h/mAh)'] = filtered_df['Screen On Time (hours/day)'] * 1000 / filtered_df['Battery Drain (mAh/day)']
eff_model = filtered_df.groupby('Device Model')['Efficiency (h/mAh)'].mean().sort_values(ascending=False).reset_index()
if not eff_model.empty:
    best_eff = eff_model.iloc[0]
    st.success(f"✅ **Maior Eficiência:** Na seleção atual, o **{best_eff['Device Model']}** é o mais eficiente, entregando em média **{best_eff['Efficiency (h/mAh)']:.2f} horas de tela para cada 1000 mAh** de bateria.")

# Insight de Correlação
corr_usage_battery = filtered_df[['App Usage Time (min/day)', 'Battery Drain (mAh/day)']].corr().iloc[0, 1]
st.info(f"🔋 **Correlação Forte:** A correlação entre o tempo de uso de apps e o consumo de bateria é de **{corr_usage_battery:.2f}**. Isso confirma que o uso de aplicativos é um grande fator no consumo de energia.")

# Insight da Análise Comparativa
try:
    avg_data_c1 = compare_df[compare_df['User Behavior Class'] == class_compare_1]['Data Usage (MB/day)'].mean()
    avg_data_c2 = compare_df[compare_df['User Behavior Class'] == class_compare_2]['Data Usage (MB/day)'].mean()
    if avg_data_c1 > 0 and not pd.isna(avg_data_c1) and not pd.isna(avg_data_c2):
        ratio = avg_data_c2 / avg_data_c1
        st.warning(f"⚖️ **Comparativo de Consumo:** Um usuário da **Classe {class_compare_2}** consome em média **{ratio:.1f}x mais dados** que um usuário da **Classe {class_compare_1}**.")
except (ZeroDivisionError, IndexError):
    pass # Ignora o insight se não for possível calcular

st.markdown("<div style='text-align: center; margin-top: 20px;'>Fim do Relatório</div>", unsafe_allow_html=True)