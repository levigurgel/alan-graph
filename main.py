import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Uso de Dispositivos Móveis",
    layout="wide"
)
st.title("Dashboard de Uso de Dispositivos Móveis e Comportamento de Usuários")

# Upload de arquivo CSV
st.sidebar.header("Carregar Dados")
uploaded_file = st.sidebar.file_uploader(
    "Selecione o arquivo CSV com os dados", type=["csv"]
)
if not uploaded_file:
    st.warning("Por favor, envie o arquivo CSV para começar a análise.")
    st.stop()

df = pd.read_csv(uploaded_file)

# Filtros interativos
st.sidebar.header("Filtrar Dados")
os_options = st.sidebar.multiselect(
    "Sistema Operacional", df["Operating System"].unique(),
    default=df["Operating System"].unique()
)
gender_options = st.sidebar.multiselect(
    "Gênero", df["Gender"].unique(),
    default=df["Gender"].unique()
)
class_options = st.sidebar.multiselect(
    "Classe de Comportamento", sorted(df["User Behavior Class"].unique()),
    default=sorted(df["User Behavior Class"].unique())
)
model_options = st.sidebar.multiselect(
    "Modelo de Dispositivo", df["Device Model"].unique(),
    default=df["Device Model"].unique()
)
# Faixas numéricas
st.sidebar.subheader("Intervalos Numéricos")
def slider(col, name):
    mn, mx = df[col].min(), df[col].max()
    return st.sidebar.slider(name, float(mn), float(mx), (float(mn), float(mx)))
usage_range = slider("App Usage Time (min/day)", "Uso de App (min/dia)")
screen_range = slider("Screen On Time (hours/day)", "Tela Ativa (h/dia)")
batt_range = slider("Battery Drain (mAh/day)", "Consumo de Bateria (mAh/dia)")
apps_range = slider("Number of Apps Installed", "Apps Instalados")
data_range = slider("Data Usage (MB/day)", "Consumo de Dados (MB/dia)")

# Aplicar filtros
filtered = df[
    df["Operating System"].isin(os_options) &
    df["Gender"].isin(gender_options) &
    df["User Behavior Class"].isin(class_options) &
    df["Device Model"].isin(model_options) &
    df["App Usage Time (min/day)"].between(*usage_range) &
    df["Screen On Time (hours/day)"].between(*screen_range) &
    df["Battery Drain (mAh/day)"].between(*batt_range) &
    df["Number of Apps Installed"].between(*apps_range) &
    df["Data Usage (MB/day)"].between(*data_range)
]

# KPI Metrics
st.subheader("Visão Geral de KPIs")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Média Uso de App (min/dia)", f"{filtered['App Usage Time (min/day)'].mean():.1f}")
col2.metric("Média Tela Ativa (h/dia)", f"{filtered['Screen On Time (hours/day)'].mean():.1f}")
col3.metric("Média Consumo Dados (MB/dia)", f"{filtered['Data Usage (MB/day)'].mean():.1f}")
col4.metric("Média Apps Instalados", f"{filtered['Number of Apps Installed'].mean():.1f}")

# Gráficos de Pizza
st.subheader("Distribuição por Sistema Operacional")
fig_os = px.pie(filtered, names="Operating System", title="Share de Sistemas Operacionais")
fig_os.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig_os, use_container_width=True)

st.subheader("Distribuição por Gênero")
fig_gen = px.pie(filtered, names="Gender", title="Share por Gênero")
fig_gen.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig_gen, use_container_width=True)

# Top 10 Modelos por Uso Médio de App (com espaçamento)
st.subheader("Top 10 Modelos por Uso Médio de App")
model_usage = (
    filtered.groupby('Device Model')['App Usage Time (min/day)']
    .mean().sort_values(ascending=False).head(10).reset_index()
)
fig_model = px.bar(model_usage, x='Device Model', y='App Usage Time (min/day)',
                   title="Uso Médio de App (min/dia) por Modelo",
                   labels={'App Usage Time (min/day)': 'Uso Médio (min/dia)'})
fig_model.update_traces(marker_line_width=1, marker_line_color='black')
fig_model.update_layout(bargap=0.3)
st.plotly_chart(fig_model, use_container_width=True)

# Matriz de Correlação
st.subheader("Matriz de Correlação entre Métricas")
numeric_cols = [
    'App Usage Time (min/day)', 'Screen On Time (hours/day)',
    'Battery Drain (mAh/day)', 'Number of Apps Installed',
    'Data Usage (MB/day)', 'Age'
]
corr = filtered[numeric_cols].corr()
fig_corr = px.imshow(corr, text_auto=True, title="Correlação de Métricas")
st.plotly_chart(fig_corr, use_container_width=True)

# Eficiência de Bateria (h tela / mAh)
st.subheader("Eficiência Energética por Modelo")
filtered['Efficiency'] = filtered['Screen On Time (hours/day)'] / filtered['Battery Drain (mAh/day)']
eff_model = (filtered.groupby('Device Model')['Efficiency']
             .mean().sort_values(ascending=False).head(10).reset_index())
fig_eff = px.bar(eff_model, x='Device Model', y='Efficiency',
                 title="Top 10 Modelos Mais Eficientes (h/mAh)",
                 labels={'Efficiency': 'Horas de Tela por mAh'})
fig_eff.update_traces(marker_line_width=1, marker_line_color='black')
fig_eff.update_layout(bargap=0.3)
st.plotly_chart(fig_eff, use_container_width=True)

# Uso por Faixa Etária e Modelo
st.subheader("Aparelhos Mais Usados por Faixa Etária")
bins = [filtered['Age'].min(), 25, 35, 50, filtered['Age'].max()]
labels = ['<=25', '26-35', '36-50', '>50']
filtered['Age Group'] = pd.cut(filtered['Age'], bins=bins, labels=labels, include_lowest=True)
age_counts = (
    filtered.groupby(['Age Group', 'Device Model'])
    .size().reset_index(name='count')
)
fig_age = px.sunburst(age_counts, path=['Age Group','Device Model'], values='count',
                     title="Uso de Dispositivos por Faixa Etária")
st.plotly_chart(fig_age, use_container_width=True)

# Insight Inteligentes (texto)
st.subheader("Insights Inteligentes")
# Modelo mais eficiente
best_eff = eff_model.iloc[0]
st.markdown(f"- Modelo **{best_eff['Device Model']}** com maior eficiência: **{best_eff['Efficiency']:.2f}** h/mAh.")
# Faixa etária mais ativa
top_age = age_counts.sort_values('count', ascending=False).iloc[0]
st.markdown(f"- Faixa etária **{top_age['Age Group']}** usa mais o modelo **{top_age['Device Model']}**.")
# Correlação forte entre uso e bateria
high_corr = corr.loc['App Usage Time (min/day)', 'Battery Drain (mAh/day)']
st.markdown(f"- Correlação entre uso de app e consumo de bateria: **{high_corr:.2f}**, indicando relação forte entre mais uso e maior drenagem.")
