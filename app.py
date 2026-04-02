import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Створення прикладу даних для скачування
example_data = """товар,кількість,дата,регіон,сума
Смартфон,10,2026-01-05,Київ,100000
Ноутбук,2,2026-01-12,Львів,70000
Навушники,25,2026-01-25,Київ,25000
Смартфон,8,2026-02-02,Одеса,80000
Мишка,40,2026-02-14,Харків,20000"""

st.sidebar.download_button(
    label="📥 Скачати приклад CSV для тесту",
    data=example_data,
    file_name='test_sales_sample.csv',
    mime='text/csv',
)
# Налаштування сторінки
st.set_page_config(page_title="E-commerce Analytics", layout="wide")

st.title("📊 Аналітика продажів e-commerce")
st.markdown("---")

# Завантаження файлу
uploaded_file = st.sidebar.file_uploader("Завантажте CSV файл", type="csv")

if uploaded_file is not None:
    # Читання даних
    df = pd.read_csv(uploaded_file)
    
    # Конвертація дати
    df['дата'] = pd.to_datetime(df['дата'])
    df['місяць'] = df['дата'].dt.to_period('M').astype(str)
    
    # Вивід сирих даних
    if st.checkbox("Показати сирі дані"):
        st.write(df.head())

    # --- Метрики (Середній чек) ---
    st.header("📈 Основні показники")
    avg_check = df['сума'].mean() if 'сума' in df.columns else (df['кількість'] * 10).mean() # Приклад розрахунку
    col1, col2 = st.columns(2)
    col1.metric("Середній чек", f"{avg_check:.2f} грн")
    col2.metric("Загальна кількість замовлень", len(df))

    # --- Pareto-аналіз (80/20) ---
    st.header("🎯 Pareto-аналіз (Товари)")
    
    # Групування за товаром
    pareto_df = df.groupby('товар')['кількість'].sum().reset_index()
    pareto_df = pareto_df.sort_values(by='кількість', ascending=False)
    pareto_df['cum_perc'] = pareto_df['кількість'].cumsum() / pareto_df['кількість'].sum() * 100

    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(x=pareto_df['товар'], y=pareto_df['кількість'], name="Кількість"))
    fig_pareto.add_trace(go.Scatter(x=pareto_df['товар'], y=pareto_df['cum_perc'], name="% Кумулятивно", yaxis="y2", line=dict(color="red")))
    
    fig_pareto.update_layout(
        title="Парето: які товари дають основний обсяг",
        yaxis=dict(title="Кількість продажів"),
        yaxis2=dict(title="Кумулятивний %", overlaying="y", side="right", range=[0, 110]),
        showlegend=True
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    # --- Продажі по регіонах та місяцях ---
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🗺 Продажі по регіонах")
        region_df = df.groupby('регіон')['кількість'].sum().reset_index()
        fig_region = px.pie(region_df, values='кількість', names='регіон', hole=0.3)
        st.plotly_chart(fig_region, use_container_width=True)

    with col4:
        st.subheader("📅 Сезонність (по місяцях)")
        monthly_df = df.groupby('місяць')['кількість'].sum().reset_index()
        fig_monthly = px.line(monthly_df, x='місяць', y='кількість', markers=True)
        st.plotly_chart(fig_monthly, use_container_width=True)

else:
    st.info("Будь ласка, завантажте CSV файл для початку аналізу.")
    st.info("Вимоги до колонок: товар, кількість, дата, регіон")
