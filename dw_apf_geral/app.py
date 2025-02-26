
import streamlit as st
import pandas as pd
#import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt

# Caminho do novo arquivo
file_3 = '/Users/luisjesus/Downloads/ORGAOS_DW_APF_GERAL.csv'


# Função para carregar e mostrar os dados
def load_data():
    # Carregar o arquivo
    df_orgaos = pd.read_csv(file_3)
    return df_orgaos

# criar subdataframes
# de orgaos superiores : unique org_padr_id, org_padr_sigla e org_padr_nome
# de orgaos subordinados : unique org_id, org_sigla e org_nome
def subdataframes(df_orgaos):
    # criar subdataframes
    # de orgaos superiores : unique org_padr_id, org_padr_sigla e org_padr_nome
    df_orgaos_superiores = df_orgaos[['ORG_PADR_ID', 'ORG_PADR_SIGLA', 'ORG_PADR_NOME']].drop_duplicates()
    # de orgaos subordinados : unique org_id, org_sigla e org_nome
    df_orgaos_subordinados = df_orgaos[['ORG_PADR_ID', 'ORG_PADR_ID.1', 'ORG_PADR_SIGLA.1', 'ORG_PADR_NOME.1', 'ORGAO_UNIFICADO_ID_ORIGEM', 'ORGAO_UNIFICADO_NOME', 'ORGAO_UNIFICADO_FONTE']].drop_duplicates()
    return df_orgaos_superiores, df_orgaos_subordinados


# função para criar o menu de filtro de orgaos a partir do org_padr_sigla do dataframe
def menu(df_orgaos_superiores):
    orgao = st.sidebar.selectbox('Selecione o Órgão:', df_orgaos_superiores[['ORG_PADR_ID', 'ORG_PADR_SIGLA', 'ORG_PADR_NOME']].apply(lambda x: f"{x['ORG_PADR_ID']} - {x['ORG_PADR_SIGLA']} - {x['ORG_PADR_NOME']}", axis=1))
    # orgao_id = orgao.split(' - ')[0]
    return orgao


def plot_graph(df_superiores, df_subordinados):
    net = Network(notebook=True, directed=True)

    # Adicionar nós de órgãos superiores
    for _, row in df_superiores.iterrows():
        net.add_node(row['ORG_PADR_ID'], label=row['ORG_PADR_SIGLA'], title=row['ORG_PADR_NOME'], color='blue')

    # Adicionar nós de órgãos subordinados e arestas
    for _, row in df_subordinados.iterrows():
        net.add_node(row['ORG_PADR_ID.1'], label=row['ORG_PADR_SIGLA.1'], title=row['ORG_PADR_NOME.1'], color='green', fonte=row['ORGAO_UNIFICADO_FONTE'])
        net.add_edge(row['ORG_PADR_ID'], row['ORG_PADR_ID.1'], title=f"Fonte: {row['ORGAO_UNIFICADO_FONTE']}")

    net.show_buttons(filter_=['physics'])
    net.show("graph.html")
    st.components.v1.html(open("graph.html", 'r', encoding='utf-8').read(), height=600)


# Função principal do Streamlit
def main():
    st.title("Visualização dos Dados dos Órgãos")
    
    # Carregar os dados
    df_orgaos = load_data()
    # Subdataframes
    df_orgaos_superiores, df_orgaos_subordinados = subdataframes(df_orgaos)
    # KPIs totais de órgãos superiores e subordinados distintos
    st.subheader("Informações Gerais")
    qtd_orgaos_superiores = df_orgaos_superiores['ORG_PADR_ID'].nunique()
    qtd_orgaos_subordinados = df_orgaos_subordinados['ORG_PADR_ID.1'].nunique()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Quantidade de Órgãos Superiores", value=qtd_orgaos_superiores)
    with col2:
        st.metric(label="Quantidade de Órgãos Subordinados", value=qtd_orgaos_subordinados)
    
    # Menu de filtro
    orgao = menu(df_orgaos_superiores)
    st.write(f"Órgão selecionado: {orgao}")

    # Filtrar os dados pelo órgão selecionado
    orgao_id = orgao.split(' - ')[0]
    df_orgaos_superiores_filtrado = df_orgaos_superiores[df_orgaos_superiores['ORG_PADR_ID'] == int(orgao_id)]
    df_orgaos_subordinados_filtrado = df_orgaos_subordinados[df_orgaos_subordinados['ORG_PADR_ID'] == int(orgao_id)]

    # kpis
    # quantidade distinto de orgaos subordinados
    qtd_orgaos_subordinados = df_orgaos_subordinados_filtrado['ORG_PADR_ID.1'].nunique()    
    st.write(f"Quantidade de Órgãos Subordinados: {qtd_orgaos_subordinados}")
    # Lista única dos órgãos subordinados
    orgaos_subordinados_unicos = df_orgaos_subordinados_filtrado[['ORG_PADR_ID.1', 'ORG_PADR_SIGLA.1', 'ORG_PADR_NOME.1']].drop_duplicates()
    # orgaos_subordinados_lista = orgaos_subordinados_unicos.apply(lambda x: f"[{x['ORG_PADR_ID.1']}] {x['ORG_PADR_SIGLA.1']} - {x['ORG_PADR_NOME.1']}", axis=1).tolist()

    # criar menu lateral para escolher o orgao subordinado único, permitindo mais de uma seleção
    orgao_subordinado = st.sidebar.multiselect(
        'Selecione o Órgão Subordinado:',
        orgaos_subordinados_unicos[['ORG_PADR_ID.1', 'ORG_PADR_SIGLA.1', 'ORG_PADR_NOME.1']].apply(lambda x: f"{x['ORG_PADR_ID.1']} - {x['ORG_PADR_SIGLA.1']} - {x['ORG_PADR_NOME.1']}", axis=1),
        default=orgaos_subordinados_unicos[['ORG_PADR_ID.1', 'ORG_PADR_SIGLA.1', 'ORG_PADR_NOME.1']].apply(lambda x: f"{x['ORG_PADR_ID.1']} - {x['ORG_PADR_SIGLA.1']} - {x['ORG_PADR_NOME.1']}", axis=1).tolist()
    )

    # sugestão de comando insert into para inserir os orgaos subordinados selecionados na tabela DM_ORGAO_UNIFICADO_NOVO


    # Filtrar os dados pelos órgãos subordinados selecionados
    orgao_subordinado_ids = [int(org.split(' - ')[0]) for org in orgao_subordinado]
    df_orgaos_subordinados_filtrado = df_orgaos_subordinados_filtrado[df_orgaos_subordinados_filtrado['ORG_PADR_ID.1'].isin(orgao_subordinado_ids)]

    st.subheader("Lista de Órgãos Subordinados Únicos")
    st.dataframe(orgaos_subordinados_unicos)
    
    # Escrever tabelas
    st.write("Dados do arquivo de Órgãos Superiores:")
    st.dataframe(df_orgaos_superiores_filtrado)
    st.write("Dados do arquivo de Órgãos Subordinados:")
    fontes = df_orgaos_subordinados_filtrado['ORGAO_UNIFICADO_FONTE'].unique()
    for fonte in fontes:
        st.write(f"Fonte: {fonte}")
        df_filtrado_por_fonte = df_orgaos_subordinados_filtrado[df_orgaos_subordinados_filtrado['ORGAO_UNIFICADO_FONTE'] == fonte]
        st.dataframe(df_filtrado_por_fonte)
        # campo para sugestão de insert que possa ser copiado

 
    # Plotar o grafo
    plot_graph(df_orgaos_superiores_filtrado, df_orgaos_subordinados_filtrado)


if __name__ == '__main__':
    main()
