import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")
# Função para carregar os dados dos arquivos Excel
def load_data(produtos_path, meses_paths):
    # Verificar se o arquivo de produtos existe
    if not os.path.exists(produtos_path):
        st.error(f"Arquivo {produtos_path} não encontrado.")
        return None, None
    
    # Carrega a planilha de produtos
    try:
        produtos_df = pd.read_csv(produtos_path, sep=";", encoding="latin1")
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo de produtos: {e}")
        return None, None

    # Carrega os dados dos meses
    meses_data = []
    for mes, file_path in meses_paths.items():
        if not os.path.exists(file_path):
            st.error(f"Arquivo {file_path} não encontrado.")
            continue

        try:
            df = pd.read_csv(file_path, sep=";", encoding="latin1")
            df.columns = ["Código", "Descrição", "Loc", "Saldo em Estoque", "Quantidade Contada", "Diferença", "Unidade", "Valor Estoque", "Valor Contada", "Diferença Valor"]
            df['Diferença Valor'] = df['Diferença Valor'].astype(str).str.replace('.', '').str.replace(',', '.').astype(float)
            df['Diferença'] = df['Diferença'].astype(str).str.replace('.', '').str.replace(',', '.').astype(float)

            df['Preço Médio'] = df['Diferença Valor'] / df['Diferença']

            df['Mês'] = mes
            meses_data.append(df)
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo {file_path}: {e}")

    if not meses_data:
        return produtos_df, pd.DataFrame()  # Retorna apenas o DataFrame de produtos se nenhum mês foi carregado com sucesso

    meses_df = pd.concat(meses_data, ignore_index=True)
    return produtos_df, meses_df

# Função para exibir os dados na interface Streamlit
def show_data(produtos_df, meses_df):

    sorter_month = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    meses_df["Mês"] = pd.Categorical(meses_df["Mês"], categories=sorter_month, ordered=True)
    

    st.title("Análise de Fechamento A&B")
    st.divider()

    produtos_unicos = meses_df["Descrição"].unique()
    meses = meses_df['Mês'].unique()

    meses_selecionados = st.sidebar.multiselect("Mes:", meses)
    produtos_selecionados = st.sidebar.multiselect("Produtos:", sorted(produtos_unicos))

    if len(produtos_selecionados) != 0:
        meses_df = meses_df.loc[meses_df['Descrição'].isin(produtos_selecionados)]

    if len(meses_selecionados) != 0:
        meses_df = meses_df.loc[meses_df['Mês'].isin(meses_selecionados)]


    # st.dataframe(produtos_df)

    if not meses_df.empty:
        # st.header("Dados Mensais [raw]")
        # st.dataframe(meses_df, hide_index=True, use_container_width=True)

        st.header("Estatísticas Gerais")
        sorter_month = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
        meses_df["Mês"] = pd.Categorical(meses_df["Mês"], categories=sorter_month, ordered=True)

        df_grouped_by_month = meses_df.groupby(["Mês"])["Diferença Valor"].sum().reset_index()
        meses_df["Mês"] = pd.Categorical(meses_df["Mês"], categories=sorter_month, ordered=True)

         #------------------------------ CURVA ABC 30 ITENS
        df_grouped_by_prod_consumo = meses_df.groupby(["Descrição"])["Diferença Valor"].sum().reset_index()

        fig_prod_2 = px.bar(df_grouped_by_prod_consumo.sort_values("Diferença Valor").head(30), 
                        x="Descrição", 
                        y="Diferença Valor", 
                        color="Descrição",
                        title="Curva ABC 30 itens",
                        orientation="v")
        
        st.plotly_chart(fig_prod_2)

        df_grouped_by_month_prod = meses_df.groupby(["Mês", "Descrição"])["Diferença Valor"].sum().reset_index()




        fig_prod_2 = px.bar(df_grouped_by_month.sort_values("Mês"), 
                        x="Mês", 
                        y="Diferença Valor", 

                        title="Total Diferenças Valor por mês",
                        orientation="v")
        col1, col2 = st.columns(2)

        col1.write("Diferenças Mes / Produto")
        col2.write("Total Diferenças por Mês")

        col2.dataframe(df_grouped_by_month, use_container_width=True, hide_index=True)
        col1.dataframe(df_grouped_by_month_prod.sort_values('Diferença Valor'), use_container_width=True, hide_index=True)
        st.plotly_chart(fig_prod_2, use_container_width=True)

        
        fig_prod_2 = px.bar(df_grouped_by_month_prod.sort_values("Mês"), 
                        x="Mês", 
                        y="Diferença Valor", 
                        color="Descrição",
                        title="Total Diferenças Valor detalhando Produtos",
                        orientation="v")
        
        st.plotly_chart(fig_prod_2, use_container_width=True,)


        df_grouped_by_month_consumo = meses_df.groupby(["Mês", "Descrição"])["Diferença"].sum().reset_index()

        fig_prod_3 = px.bar(df_grouped_by_month_consumo.sort_values("Mês"), 
                        x="Mês", 
                        y="Diferença", 
                        color="Descrição",
                        title="Total Consumos detalhando Produtos / unidade Medida",
                        orientation="v")
        
        st.plotly_chart(fig_prod_3, use_container_width=True,)

       

        #-----------------------------PREÇOS
        df_grouped_by_month_prod = meses_df.groupby(["Mês", "Descrição"])["Preço Médio"].mean().reset_index()
        fig_prod_4 = px.bar(df_grouped_by_month_prod.sort_values("Mês"), 
                        x="Mês", 
                        y="Preço Médio", 
                        color="Descrição",
                        title="Preço Médio / Unidade",
                        orientation="v")
        
        st.plotly_chart(fig_prod_4, use_container_width=True,)

        st.divider()
        st.header("Dados Mensais [raw]")
        st.dataframe(meses_df, hide_index=True, use_container_width=True)
        total_diferenca_valor = meses_df["Diferença Valor"].sum()
        st.write(f"Total Diferença em Valor: R$ {total_diferenca_valor}")



# Função principal para rodar a aplicação
def main():
    # Caminhos dos arquivos
    produtos_path = 'dados/produtos.csv'
    meses_paths = {
        'jan': 'dados/jan.csv',
        'fev': 'dados/fev.CSV',
        'mar': 'dados/mar.CSV',
        'abr': 'dados/abr.CSV',
        'mai': 'dados/mai.CSV',
        'jun': 'dados/jun.CSV',
        # Adicione os outros meses aqui
    }

    # Carregar os dados
    produtos_df, meses_df = load_data(produtos_path, meses_paths)

    if produtos_df is not None and not meses_df.empty:
        # Mostrar os dados na interface Streamlit
        show_data(produtos_df, meses_df)
    else:
        st.error("Erro ao carregar os dados. Verifique os arquivos e tente novamente.")

if __name__ == "__main__":
    main()
