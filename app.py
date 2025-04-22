import streamlit as st
import pandas as pd
from io import BytesIO

# Função para converter tipos apenas onde faz sentido
def converter_tipos(df):
    for col in df.select_dtypes(include='object').columns:
        try:
            df[col] = pd.to_datetime(df[col], errors='ignore')
        except:
            pass
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors='ignore')
        except:
            pass
    return df

# Cache para leitura de arquivos
@st.cache_data
def ler_excel(uploaded_file):
    return pd.read_excel(uploaded_file, sheet_name=None)

# Configurações da página
st.set_page_config(page_title="Cruzadex", layout="wide")
st.title("🔗 **Cruzadex** – A ponte entre suas planilhas e a produtividade.")

# Instruções
with st.expander("📘 Como usar o Cruzadex"):
    st.markdown("""
    ### 🛠️ Passo a passo para usar o Cruzadex:

    - 📂 **Envie um ou mais arquivos** `.xlsx` com **uma ou mais abas** cada.
    - 🔑 **Informe a coluna-chave** para o cruzamento dos dados (ex: `codigo_produto`, `id_cliente`).
    - 📌 **Escolha as colunas** que deseja trazer de cada aba (além da chave).
    - 🔀 **Escolha o tipo de junção** (outer, inner, left, right).
    - 👀 Veja uma **prévia das colunas, tipos e dados** antes de cruzar.
    - 🚀 Clique em **“Cruzar Dados”** para iniciar a mágica!
    - 📥 **Baixe o resultado final** em Excel com os dados cruzados!

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
        abas[uploaded_file.name] = ler_excel(uploaded_file)
        nomes_abas.extend(list(abas[uploaded_file.name].keys()))
    
    nomes_abas = sorted(set(nomes_abas))
    st.success(f"✅ {len(nomes_abas)} abas encontradas em {len(uploaded_files)} arquivos.")

    # Prévia visual das abas e colunas
    st.subheader("👁️ Pré-visualização das abas e colunas")
    for nome_arquivo, abas_arquivo in abas.items():
        with st.expander(f"📂 Arquivo: `{nome_arquivo}`"):
            for nome_aba, df in abas_arquivo.items():
                st.markdown(f"🔹 **Aba:** `{nome_aba}` | **{df.shape[0]} linhas, {df.shape[1]} colunas**")
                st.code(', '.join([f"{col} ({df[col].dtype})" for col in df.columns]), language='markdown')
                st.dataframe(df.head(5), use_container_width=True)

    # Coluna-chave e tipo de junção
    coluna_chave = st.text_input("🔑 Qual o nome da coluna-chave para cruzar os dados?")
    tipo_juncao = st.selectbox("🔀 Tipo de junção:", ["outer", "inner", "left", "right"])

    if coluna_chave:
        colunas_disponiveis = set()
        for abas_arquivo in abas.values():
            for df in abas_arquivo.values():
                df = converter_tipos(df)
                colunas_disponiveis.update(df.columns)

        colunas_disponiveis = sorted(list(colunas_disponiveis))
        colunas_escolhidas_globais = st.multiselect(
            "📌 Selecione as colunas para cruzar (exceto a chave)",
            options=[col for col in colunas_disponiveis if col != coluna_chave],
            default=["valor"] if "valor" in colunas_disponiveis else []
        )

        if st.button("🚀 Cruzar Dados"):
            resultado = None
            log_abas = []

            for nome_arquivo, abas_arquivo in abas.items():
                for nome_aba, df in abas_arquivo.items():
                    if coluna_chave not in df.columns:
                        continue

                    df = converter_tipos(df)
                    colunas_validas = [col for col in colunas_escolhidas_globais if col in df.columns]
                    colunas_para_usar = [coluna_chave] + colunas_validas
                    df = df[colunas_para_usar]

                    df.rename(columns={
                        col: f"{col}_{nome_aba}_{nome_arquivo}" if col != coluna_chave else col
                        for col in df.columns
                    }, inplace=True)

                    if resultado is None:
                        resultado = df
                    else:
                        resultado = resultado.merge(df, on=coluna_chave, how=tipo_juncao)

                    log_abas.append(f"{nome_aba} ({nome_arquivo})")

            if resultado is not None and not resultado.empty:
                st.success("✅ Dados cruzados com sucesso!")
                st.dataframe(resultado, use_container_width=True)

                # Histórico de cruzamento
                st.markdown("📝 **Histórico das abas cruzadas:**")
                st.write(log_abas)

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
