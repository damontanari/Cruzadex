import streamlit as st
import pandas as pd
from io import BytesIO
import stripe
import streamlit_authenticator as stauth

# Função para configurar o design
def configurar_design():
    st.markdown(
        """
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #f5f5f5;
            }
            .title {
                color: #003366;
                font-size: 32px;
                font-weight: bold;
            }
            .btn-primary {
                background-color: #0066cc;
                color: white;
            }
            .btn-primary:hover {
                background-color: #005bb5;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

# Função para identificar e converter os tipos de dados
def converter_tipos(df):
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

# Função para cruzamento de dados
def cruzar_dados(abas, coluna_chave, colunas_escolhidas_globais):
    resultado = None
    for nome_aba, df in abas.items():
        if coluna_chave not in df.columns:
            continue

        # Converte os tipos de dados da aba atual
        df = converter_tipos(df)

        # Filtra as colunas que o usuário escolheu
        colunas_validas = [col for col in colunas_escolhidas_globais if col in df.columns]
        colunas_para_usar = [coluna_chave] + colunas_validas
        df = df[colunas_para_usar]

        # Renomeia as colunas para identificar de qual aba vem
        df = df.rename(columns={
            col: f"{col}_{nome_aba}" if col != coluna_chave else col
            for col in df.columns
        })

        # Faz o merge com o resultado acumulado
        if resultado is None:
            resultado = df
        else:
            resultado = resultado.merge(df, on=coluna_chave, how="outer")

    return resultado

# Configurações da página
st.set_page_config(page_title="Cruzadex – Cruzamento de Planilhas", layout="wide")
configurar_design()

# Definindo credenciais de autenticação como um dicionário correto
credentials = {
    'usernames': {
        'user1': {
            'name': 'User 1',
            'password': 'password1'
        },
        'user2': {
            'name': 'User 2',
            'password': 'password2'
        }
    }
}

# Inicializa o Streamlit Authenticator
authenticator = stauth.Authenticate(credentials)

# Login
if authenticator.login('Login', location='main'):  # Aqui a localização deve ser 'main' ou 'sidebar'
    st.write(f"Bem-vindo {authenticator.username}!")
    
    # Upload do arquivo Excel
    uploaded_file = st.file_uploader("📤 Envie um arquivo Excel com várias abas", type=["xlsx"])

    if uploaded_file:
        abas = pd.read_excel(uploaded_file, sheet_name=None)
        nomes_abas = list(abas.keys())
        st.success(f"✅ {len(nomes_abas)} abas encontradas.")

        # Solicita a coluna-chave para cruzamento
        coluna_chave = st.text_input("🧩 Digite a coluna para cruzamento (ex: codigo_produto)")

        if coluna_chave:
            # Coleta todas as colunas disponíveis em todas as abas
            colunas_disponiveis = set()
            for df in abas.values():
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
                resultado = cruzar_dados(abas, coluna_chave, colunas_escolhidas_globais)

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

else:
    st.warning("Por favor, faça o login para continuar.")

# Exemplo de Código para Anúncios (Google AdSense)
st.markdown(
    """
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-XXXXXX"
         data-ad-slot="XXXXXX"
         data-ad-format="auto"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
    """,
    unsafe_allow_html=True
)

# Configuração do Stripe para plano Premium
stripe.api_key = "sua_chave_secreta_da_stripe"

def criar_plano_premium():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Plano Premium Cruzadex',
                },
                'unit_amount': 1000,  # Preço em centavos
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://seusite.com/sucesso',
        cancel_url='https://seusite.com/cancelar',
    )
    return session.url

# Botão para redirecionamento para o plano Premium
if st.button('💳 Adquirir Plano Premium'):
    plano_url = criar_plano_premium()
    st.markdown(f"🎉 **Clique [aqui]({plano_url}) para acessar o Plano Premium**")
