import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pandas as pd

def gerar_graficos(df, tamanho="Médio"):
    """
    Função que gera gráficos com base nas colunas do DataFrame.
    Adaptado para diferentes tipos de dados e cruzamentos.
    Tamanho ajustável dos gráficos.
    """
    # Definir o estilo do gráfico para um visual mais profissional
    sns.set(style="whitegrid")

    # Ajustar o tamanho do gráfico conforme o parâmetro 'tamanho'
    if tamanho == "Pequeno":
        fig_size = (6, 4)  # Gráficos menores
    elif tamanho == "Grande":
        fig_size = (12, 7)  # Gráficos maiores
    else:
        fig_size = (8, 5)  # Tamanho médio padrão

    # Gráfico de Distribuição: Histograma (caso existam colunas numéricas)
    colunas_numericas = df.select_dtypes(include=['number']).columns
    if len(colunas_numericas) > 0:
        for col in colunas_numericas:
            st.subheader(f"🔹 Histograma de {col}")
            fig, ax = plt.subplots(figsize=fig_size)  # Tamanho ajustado para tela
            sns.histplot(df[col], kde=True, ax=ax, color='dodgerblue', bins=20)
            ax.set_title(f"Distribuição de {col}", fontsize=16, fontweight='bold')
            ax.set_xlabel(col, fontsize=12)
            ax.set_ylabel('Frequência', fontsize=12)
            plt.tight_layout()  # Ajuste do layout para evitar sobreposição
            st.pyplot(fig)

    # Gráficos de barras para dados categóricos
    colunas_categoricas = df.select_dtypes(include=['object', 'category']).columns
    if len(colunas_categoricas) > 0:
        for col in colunas_categoricas:
            st.subheader(f"🔹 Gráfico de barras: {col}")
            fig, ax = plt.subplots(figsize=fig_size)  # Tamanho ajustado para tela
            df[col].value_counts().plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
            ax.set_title(f"Distribuição de {col}", fontsize=16, fontweight='bold')
            ax.set_xlabel(col, fontsize=12)
            ax.set_ylabel('Contagem', fontsize=12)
            plt.tight_layout()  # Ajuste do layout para evitar sobreposição
            st.pyplot(fig)

    # Gráfico de dispersão: Relacionamento entre duas colunas numéricas
    if len(colunas_numericas) >= 2:
        for i in range(len(colunas_numericas)):
            for j in range(i + 1, len(colunas_numericas)):
                col1 = colunas_numericas[i]
                col2 = colunas_numericas[j]
                st.subheader(f"🔹 Gráfico de Dispersão: {col1} vs {col2}")
                fig, ax = plt.subplots(figsize=fig_size)  # Tamanho ajustado para tela
                sns.scatterplot(data=df, x=col1, y=col2, ax=ax, color='orange', edgecolor='black')
                ax.set_title(f"{col1} vs {col2}", fontsize=16, fontweight='bold')
                ax.set_xlabel(col1, fontsize=12)
                ax.set_ylabel(col2, fontsize=12)
                plt.tight_layout()  # Ajuste do layout para evitar sobreposição
                st.pyplot(fig)

    # Caso haja datas, pode-se gerar um gráfico de séries temporais (lineplot)
    if 'data' in df.columns:
        st.subheader("🔹 Gráfico de Vendas ao Longo do Tempo")
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        if df['data'].isnull().sum() < len(df):
            df_sorted = df.groupby('data').size().reset_index(name='count')
            fig, ax = plt.subplots(figsize=fig_size)  # Tamanho ajustado para tela
            sns.lineplot(data=df_sorted, x='data', y='count', ax=ax, color='green')
            ax.set_title("Contagem de Registros ao Longo do Tempo", fontsize=16, fontweight='bold')
            ax.set_xlabel('Data', fontsize=12)
            ax.set_ylabel('Contagem', fontsize=12)
            plt.tight_layout()  # Ajuste do layout para evitar sobreposição
            st.pyplot(fig)
