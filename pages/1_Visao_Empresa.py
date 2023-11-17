# Libraries
import pandas as pd
import folium
import plotly_express as px
from haversine import haversine
from PIL import Image
import datetime
import streamlit as st
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

# ---------------------------
# Funções
# ---------------------------

# Função de limpeza dos dados
def clean_code(df1):
    """Esta função tem a responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remoção de dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável)

        Input: Dataframe
        Output: Dataframe
    """
    # Tratando a base
    # Convertendo idade de texto para int
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # tirando o NaN do Road_traffic_density
    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # tirando o NaN do City
    linhas_selecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # tirando o NaN do Festival
    linhas_selecionadas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # Convertendo a coluna ratings de texto para número decimal
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(
        float)

    # Convertendo a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # Convertendo multiple_deliveries de texto para int
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # Comando para remover o texte de números
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(
        lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    # removendo os espaços dentro de strings/texto/object
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:,
                                                 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    return df1


def order_metric(df1):
    """Função que calcula a quantidade de pedidos diárias a partir do dataframe"""
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby(
        'Order_Date').count().reset_index()

    # desenhar gráfico de barras
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig


def traffic_order_share(df1):
    """Esta função calcula a quantidade de pedidos por densidade de tráfego"""
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
              .groupby('Road_traffic_density')
              .count()
              .reset_index())
    # Criando coluna de representatividade
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    # Gráfico de pizza
    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
    # Criando coluna de representatividade
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    # Gráfico de pizza
    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig


def traffic_order_city(df1):
    """ Esta função calcula a quantidade de pedidos por cidade e tipo de tráfego"""
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
              .groupby(['City', 'Road_traffic_density'])
              .count()
              .reset_index())

    # Gráfico de bolhas
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density',
                     size='ID', color='City')
    return fig


def order_by_week(df1):
    """Esta função calcula a a quantidade de pedidos realizados por semana"""
    # Criando a coluna semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    # Cálculo da quantidade de pedidos por semana
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby(
        'week_of_year').count().reset_index()

    # Criando o gráfico de linhas
    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig


def order_share_by_week(df1):
    """Esta função calcula a quantidade média de pedidos por entregadores únicos e mostra a visão por semana do ano """
    # Cálculo da quantidade de pedidos por semana
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby(
        'week_of_year').count().reset_index()

    # Quantidade de entregadores únicos por semana
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']
                       ].groupby('week_of_year').nunique().reset_index()

    df_aux = pd.merge(df_aux01, df_aux02, how='inner')

    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    # Gráfico de linhas
    fig = px.line(df_aux, x='week_of_year', y='order_by_delivery')

    return fig


def country_maps(df1):
    """Esta função cria um gráfico, plotando a localização dos locais de entrega por meio do cálculo da mediana da localização
     Os pontos do mapa são mostrados indicando a Cidade e a densidade de tráfego.
       """
    # Mediana da latitude e longitude agrupadas por cidade e tipo de tráfego
    df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
              .groupby(['City', 'Road_traffic_density'])
              .median()
              .reset_index())
    # Ciando mapa com folium
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([
            location_info['Delivery_location_latitude'],
            location_info['Delivery_location_longitude']
        ], popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width=1024, height=600)

# --------------------------- Início da estrutura lógica do código ---------------------------


# ---------------------------
# Import Dataset
# ---------------------------
df = pd.read_csv('train.csv')
# ---------------------------
# Limpando dados
# ---------------------------
df1 = clean_code(df)

# Visão Empresa
st.header('Marketplace - Visão Cliente')

# =====================================
# Barra Lateral
# =====================================

# Logo Cury Company da barra lateral
image_path = 'food_delivery.png'
image = Image.open(image_path)
# Markdown Slogan Cury Company
st.sidebar.image(image,  width=150)
st.sidebar.markdown('# :orange[**Cury Company**]')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""---""")

# Filtro Data
date_slider = st.sidebar.slider(
    'Selecione até qual data',
    value=datetime.datetime(2022, 4, 13),
    min_value=datetime.datetime(2022, 2, 11),
    max_value=datetime.datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)
# Filtro Condições de trânsito
traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)
# Aplicação dos filtros de data e tráfego
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# =====================================
# Layout no Streamlit
# =====================================

tab1, tab2, tab3 = st.tabs(
    ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        fig = order_metric(df1)
        st.markdown('### Orders by day')
        st.plotly_chart(fig, use_conatiner_width=True)

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            fig = traffic_order_share(df1)
            st.markdown('### Traffic Order Share')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('### Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('### Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('### Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('### Country Maps')
    country_maps(df1)