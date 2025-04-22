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
st.set_page_config(page_title="Cruzador de Planilhas", layout="wide")
st.title("🔗 Cruzadex – A ponte entre suas planilhas e a produtividade.")

# Instruções para o usuário
with st.expander("ℹ️ Instruções para uso"):
    st.markdown("""
    - ✅ Envie um ou mais arquivos `.xlsx` contendo uma ou mais abas cada.
    - 🧩 **A coluna usada como chave para cruzamento deve ter exatamente o mesmo nome em todas as abas e arquivos.**
    - 💡 Exemplo de chave: `codigo_produto`, `id_cliente`, etc.
    - 📌 Após digitar o nome da chave, você poderá escolher quais colunas deseja trazer de cada aba.
    - ⚠️ Se uma aba não tiver a coluna-chave exata, ela será ignorada no cruzamento.
    - 📥 Ao final, você poderá baixar o arquivo Excel com os dados cruzados.
    """)

# Upload de múltiplos arquivos Excel
uploaded_files = st.file_uploader(
    "📤 Envie um ou mais arquivos Excel com várias abas",
    type=["xlsx"],
    accept_multiple_files=True
)

# Quando os arquivos forem enviados
if uploaded_files:
    abas = {}
    nomes_abas = []

    # Lê as abas de todos os arquivos enviados
    for uploaded_file in uploaded_files:
        abas[uploaded_file.name] = pd.read_excel(uploaded_file, sheet_name=None)
        nomes_abas.extend(list(abas[uploaded_file.name].keys()))
    
    nomes_abas = sorted(set(nomes_abas))  # Remove abas duplicadas
    st.success(f"✅ {len(nomes_abas)} abas encontradas em {len(uploaded_files)} arquivos.")

    # Exibe uma prévia das colunas de cada aba de cada arquivo
    st.subheader("👀 Prévia das colunas de cada aba:")
    for nome_arquivo, abas_arquivo in abas.items():
        st.write(f"📂 **Arquivo**: {nome_arquivo}")
        for nome_aba, df in abas_arquivo.items():
            st.write(f"📊 **{nome_aba}**:")
            st.write(df.columns.tolist())

    # Solicita a coluna-chave para cruzamento
    coluna_chave = st.text_input("🧩 Digite a coluna para cruzamento (ex: codigo_produto)")

    if coluna_chave:
        # Coleta todas as colunas disponíveis em todas as abas
        colunas_disponiveis = set()
        for abas_arquivo in abas.values():
            for df in abas_arquivo.values():
                df = converter_tipos(df)
                colunas_disponiveis.update(df.columns)

        colunas_disponiveis = sorted(list(colunas_disponiveis))

        # Seleção de colunas a serem trazidas no cruzamento
        st.subheader("📌 Escolha quais colunas deseja trazer das outras abas:")
        colunas_escolhidas_globais = st.multiselect(
            "Selecione as colunas que quer trazer de cada aba (exceto a chave)",
            options=[col for col in colunas_disponiveis if col != coluna_chave],
            default=["valor"] if "valor" in colunas_disponiveis else []
        )

        # Botão para cruzar os dados
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

                    # Renomeia colunas para evitar conflitos
                    df = df.rename(columns={
                        col: f"{col}_{nome_aba}_{nome_arquivo}" if col != coluna_chave else col
                        for col in df.columns
                    })

                    if resultado is None:
                        resultado = df
                    else:
                        resultado = resultado.merge(df, on=coluna_chave, how="outer")

            # Exibe e exporta resultado
            if resultado is not None and not resultado.empty:
                st.success("✅ Cruzamento realizado com sucesso!")
                st.dataframe(resultado)

                output = BytesIO()
                resultado.to_excel(output, index=False, engine="openpyxl")
                st.download_button(
                    label="📥 Baixar Resultado como Excel",
                    data=output.getvalue(),
                    file_name="resultado_cruzado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("⚠️ Não foi possível cruzar. Verifique se todas as abas contêm a coluna-chave.")
