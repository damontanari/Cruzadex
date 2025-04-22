import streamlit as st
import pandas as pd
from io import BytesIO

# Função para identificar e converter os tipos de dados
def converter_tipos(df):
    for col in df.columns:
        if df[col].dtype == 'O':
            try:
                df[col] = pd.to_datetime(df[col], errors='ignore')
            except:
                pass
        try:
            df[col] = pd.to_numeric(df[col], errors='ignore')
        except:
            pass
    return df

# Configurações da página
st.set_page_config(page_title="Cruzadex", layout="wide")
st.title("🔗 **Cruzadex** – A ponte entre suas planilhas e a produtividade.")

# Instruções
with st.expander("📘 Como usar o Cruzadex"):
    st.markdown("""
    ### 🛠️ Passo a passo para usar o Cruzadex:

    - 📂 **Envie um ou mais arquivos** `.xlsx` com **uma ou mais abas** cada.
    - 🔑 **Informe a coluna-chave** para o cruzamento dos dados (ex: `codigo_produto`, `id_cliente`).
    - ⚠️ **Atenção!** O nome da coluna-chave **deve estar igual** em todas as abas/arquivos.
    - 📌 **Escolha as colunas** que deseja trazer de cada aba (além da chave).
    - 👀 Veja uma **prévia das colunas e dados** antes de cruzar.
    - 🚀 Clique em **“Cruzar Dados”** para iniciar a mágica!
    - 📥 **Baixe o resultado final** em formato Excel com os dados cruzados!

    ---
    💡 **Dica:** Quanto mais organizada sua planilha estiver, melhor será o resultado!
    """)


# Upload
uploaded_files = st.file_uploader(
    "📤 Envie um ou mais arquivos Excel",
    type=["xlsx"],
    accept_multiple_files=True
)

if uploaded_files:
    abas = {}
    nomes_abas = []

    for uploaded_file in uploaded_files:
        abas[uploaded_file.name] = pd.read_excel(uploaded_file, sheet_name=None)
        nomes_abas.extend(list(abas[uploaded_file.name].keys()))
    
    nomes_abas = sorted(set(nomes_abas))
    st.success(f"✅ {len(nomes_abas)} abas encontradas em {len(uploaded_files)} arquivos.")

    # Prévia visual das abas
    st.subheader("👁️ Pré-visualização das abas e colunas")
    for nome_arquivo, abas_arquivo in abas.items():
        with st.expander(f"📂 Arquivo: `{nome_arquivo}`"):
            for nome_aba, df in abas_arquivo.items():
                st.markdown(f"🔹 **Aba:** `{nome_aba}` | **{df.shape[0]} linhas**")
                st.code(', '.join(df.columns.tolist()), language='markdown')
                st.dataframe(df.head(5), use_container_width=True)

    # Coluna-chave
    coluna_chave = st.text_input("🔑 Qual o nome da coluna-chave para cruzar os dados?")

    if coluna_chave:
        colunas_disponiveis = set()
        for abas_arquivo in abas.values():
            for df in abas_arquivo.values():
                df = converter_tipos(df)
                colunas_disponiveis.update(df.columns)

        colunas_disponiveis = sorted(list(colunas_disponiveis))

        st.subheader("📌 Selecione as colunas para cruzar (exceto a chave)")
        colunas_escolhidas_globais = st.multiselect(
            "Colunas disponíveis:",
            options=[col for col in colunas_disponiveis if col != coluna_chave],
            default=["valor"] if "valor" in colunas_disponiveis else []
        )

        if st.button("🚀 Cruzar Dados"):
            resultado = None
            for nome_arquivo, abas_arquivo in abas.items():
                for nome_aba, df in abas_arquivo.items():
                    if coluna_chave not in df.columns:
                        continue

                    df = converter_tipos(df)
                    colunas_validas = [col for col in colunas_escolhidas_globais if col in df.columns]
                    colunas_para_usar = [coluna_chave] + colunas_validas
                    df = df[colunas_para_usar]

                    df = df.rename(columns={
                        col: f"{col}_{nome_aba}_{nome_arquivo}" if col != coluna_chave else col
                        for col in df.columns
                    })

                    if resultado is None:
                        resultado = df
                    else:
                        resultado = resultado.merge(df, on=coluna_chave, how="outer")

            if resultado is not None and not resultado.empty:
                st.success("✅ Dados cruzados com sucesso!")
                st.dataframe(resultado, use_container_width=True)

                output = BytesIO()
                resultado.to_excel(output, index=False, engine="openpyxl")
                st.download_button(
                    label="📥 Baixar Resultado como Excel",
                    data=output.getvalue(),
                    file_name="resultado_cruzado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("⚠️ Nenhuma aba válida para cruzamento encontrada.")
