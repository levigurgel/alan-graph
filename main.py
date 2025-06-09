import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

st.set_page_config(page_title="📊 Dashboard Mobile BI", layout="wide")
st.markdown("## 📱 Dashboard de Uso de Dispositivos Móveis e Comportamento de Usuários")
st.markdown("---")

# Sidebar - Upload
@st.cache_data
def load_data():
    df = pd.read_csv("user_behavior_dataset.csv")
    return df

df = load_data()

# Colunas obrigatórias
required_columns = [
    "Operating System", "Gender", "User Behavior Class", "Device Model",
    "App Usage Time (min/day)", "Screen On Time (hours/day)",
    "Battery Drain (mAh/day)", "Number of Apps Installed",
    "Data Usage (MB/day)", "Age"
]
missing_cols = [col for col in required_columns if col not in df.columns]
if missing_cols:
    st.error(f"Colunas ausentes no CSV: {', '.join(missing_cols)}")
    st.stop()

# Filtros
st.sidebar.header("🎛️ Filtros Interativos")
os_options = st.sidebar.multiselect("Sistema Operacional", df["Operating System"].unique(), default=df["Operating System"].unique())
gender_options = st.sidebar.multiselect("Gênero", df["Gender"].unique(), default=df["Gender"].unique())
class_options = st.sidebar.multiselect("Classe Comportamental", sorted(df["User Behavior Class"].unique()), default=sorted(df["User Behavior Class"].unique()))
model_options = st.sidebar.multiselect("Modelo de Dispositivo", df["Device Model"].unique(), default=df["Device Model"].unique())

st.sidebar.subheader("📉 Intervalos Numéricos")
def slider(col, name): return st.sidebar.slider(name, float(df[col].min()), float(df[col].max()), (float(df[col].min()), float(df[col].max())))

usage_range = slider("App Usage Time (min/day)", "Uso de App (min/dia)")
screen_range = slider("Screen On Time (hours/day)", "Tela Ativa (h/dia)")
batt_range = slider("Battery Drain (mAh/day)", "Drenagem de Bateria")
apps_range = slider("Number of Apps Installed", "Número de Apps")
data_range = slider("Data Usage (MB/day)", "Uso de Dados")

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

if filtered.empty:
    st.warning("Nenhum dado encontrado com os filtros aplicados.")
    st.stop()

# KPIs
st.markdown("### 📌 Visão Geral")
col1, col2, col3, col4 = st.columns(4)
col1.metric("📱 Uso Médio de App", f"{filtered['App Usage Time (min/day)'].mean():.1f} min")
col2.metric("🕒 Tela Ativa", f"{filtered['Screen On Time (hours/day)'].mean():.1f} h")
col3.metric("🌐 Uso de Dados", f"{filtered['Data Usage (MB/day)'].mean():.1f} MB")
col4.metric("📦 Apps Instalados", f"{filtered['Number of Apps Installed'].mean():.1f}")

# Seções de gráficos
with st.expander("📊 Distribuições Categóricas", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        fig_os = px.pie(filtered, names="Operating System", title="Distribuição por SO", color_discrete_sequence=px.colors.sequential.Plasma)
        fig_os.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_os, use_container_width=True)

    with c2:
        fig_gen = px.pie(filtered, names="Gender", title="Distribuição por Gênero", color_discrete_sequence=px.colors.sequential.Mint)
        fig_gen.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_gen, use_container_width=True)

with st.expander("🏆 Top 10 Modelos por Uso de App"):
    model_usage = filtered.groupby('Device Model')['App Usage Time (min/day)'].mean().sort_values(ascending=False).head(10).reset_index()
    fig_model = px.bar(model_usage, x='Device Model', y='App Usage Time (min/day)', title="Uso Médio de App (min/dia)", color='App Usage Time (min/day)', color_continuous_scale='Blues')
    st.plotly_chart(fig_model, use_container_width=True)

with st.expander("🔋 Eficiência Energética por Modelo"):
    filtered['Efficiency'] = filtered['Screen On Time (hours/day)'] / filtered['Battery Drain (mAh/day)']
    eff_model = filtered.groupby('Device Model')['Efficiency'].mean().sort_values(ascending=False).head(10).reset_index()
    fig_eff = px.bar(eff_model, x='Device Model', y='Efficiency', title="Eficiência: Horas de Tela por mAh", color='Efficiency', color_continuous_scale='Greens')
    st.plotly_chart(fig_eff, use_container_width=True)

with st.expander("📈 Correlação entre Variáveis Numéricas"):
    numeric_cols = ['App Usage Time (min/day)', 'Screen On Time (hours/day)', 'Battery Drain (mAh/day)', 'Number of Apps Installed', 'Data Usage (MB/day)', 'Age']
    corr_matrix = filtered[numeric_cols].corr().round(2)
    z = corr_matrix.values
    x = list(corr_matrix.columns)
    y = list(corr_matrix.index)
    fig_heatmap = ff.create_annotated_heatmap(z, x=x, y=y, annotation_text=[[f"{v:.2f}" for v in row] for row in z], colorscale='Viridis', showscale=True)
    fig_heatmap.update_layout(margin=dict(l=20, r=20, t=30, b=20), font=dict(size=12))
    st.plotly_chart(fig_heatmap, use_container_width=True)

with st.expander("🌞 Uso por Faixa Etária e Modelo"):
    bins = [filtered['Age'].min(), 25, 35, 50, filtered['Age'].max()]
    labels = ['<=25', '26-35', '36-50', '>50']
    filtered['Age Group'] = pd.cut(filtered['Age'], bins=bins, labels=labels, include_lowest=True)
    age_counts = filtered.groupby(['Age Group', 'Device Model']).size().reset_index(name='count')
    fig_age = px.sunburst(age_counts, path=['Age Group', 'Device Model'], values='count', title="Dispositivos por Faixa Etária")
    st.plotly_chart(fig_age, use_container_width=True)

# Insights
st.markdown("### 💡 Insights Inteligentes")
best_eff = eff_model.iloc[0]
top_age = age_counts.sort_values('count', ascending=False).iloc[0]
high_corr = corr_matrix.loc['App Usage Time (min/day)', 'Battery Drain (mAh/day)']

st.success(f"📌 O modelo **{best_eff['Device Model']}** é o mais eficiente com **{best_eff['Efficiency']:.2f} h/mAh**.")
st.info(f"👥 A faixa **{top_age['Age Group']}** usa mais o modelo **{top_age['Device Model']}**.")
st.warning(f"🔋 Correlação entre uso de app e consumo de bateria é **{high_corr:.2f}** (forte).")
