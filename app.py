import streamlit as st
import pandas as pd
from io import BytesIO

# Função para identificar e converter os tipos de dados
def converter_tipos(df):
    # Converte as colunas para data
    for col in df.columns:
        if df[col].dtype == 'O':  # Se a coluna for do tipo objeto (string)
            try:
                df[col] = pd.to_datetime(df[col], errors='ignore')  # Tenta converter para data
            except:
                pass  # Caso não consiga, deixa como string
        try:
            df[col] = pd.to_numeric(df[col], errors='ignore')  # Tenta converter para numérico
        except:
            pass  # Caso não consiga, deixa como está
    return df

# Configurações da página
st.set_page_config(page_title="Cruzador de Planilhas", layout="wide")
st.title("🔗 Cruzadex – A ponte entre suas planilhas e a produtividade.")

# Upload do arquivo Excel
uploaded_file = st.file_uploader("📤 Envie um arquivo Excel com várias abas", type=["xlsx"])

# Quando o arquivo for enviado
if uploaded_file:
    # Lê as abas do Excel
    abas = pd.read_excel(uploaded_file, sheet_name=None)
    nomes_abas = list(abas.keys())
    st.success(f"✅ {len(nomes_abas)} abas encontradas.")

    # Exibe uma prévia das colunas de cada aba
    st.subheader("👀 Prévia das colunas de cada aba:")
    for nome_aba, df in abas.items():
        st.write(f"📊 **{nome_aba}**:")
        st.write(df.columns.tolist())  # Exibe as colunas da aba

    # Solicita a coluna-chave para cruzamento
    coluna_chave = st.text_input("🧩 Digite a coluna para cruzamento (ex: codigo_produto)")

    if coluna_chave:
        # Coleta todas as colunas disponíveis em todas as abas
        colunas_disponiveis = set()
        for df in abas.values():
            # Converte os tipos das colunas de cada aba
            df = converter_tipos(df)
            colunas_disponiveis.update(df.columns)

        colunas_disponiveis = sorted(list(colunas_disponiveis))

        # Exibe para o usuário as opções de colunas a serem selecionadas
        st.subheader("📌 Escolha quais colunas deseja trazer das outras abas:")
        colunas_escolhidas_globais = st.multiselect(
            "Selecione as colunas que quer trazer de cada aba (exceto a chave)",
            options=[col for col in colunas_disponiveis if col != coluna_chave],
            default=["valor"] if "valor" in colunas_disponiveis else []
        )

        # Botão para realizar o cruzamento
        if st.button("🚀 Cruzar Dados"):
            resultado = None
            # Itera pelas abas para fazer o cruzamento
            for nome_aba, df in abas.items():
                if coluna_chave not in df.columns:
                    continue

                # Converte os tipos de dados para a aba atual
                df = converter_tipos(df)

                # Filtra as colunas que o usuário escolheu
                colunas_validas = [col for col in colunas_escolhidas_globais if col in df.columns]
                colunas_para_usar = [coluna_chave] + colunas_validas
                df = df[colunas_para_usar]

                # Renomeia as colunas para identificar de qual aba vem
                df = df.rename(columns={col: f"{col}_{nome_aba}" if col != coluna_chave else col
                                        for col in df.columns})

                # Faz o merge com o resultado acumulado
                if resultado is None:
                    resultado = df
                else:
                    resultado = resultado.merge(df, on=coluna_chave, how="outer")

            # Exibe o resultado e permite o download
            if resultado is not None and not resultado.empty:
                st.success("✅ Cruzamento realizado com sucesso!")
                st.dataframe(resultado)

                # Para download como Excel
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
