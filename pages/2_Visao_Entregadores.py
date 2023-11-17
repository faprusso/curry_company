import pandas as pd
import folium
import plotly_express as px
from haversine import haversine
import streamlit as st
from PIL import Image
import datetime
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='🛵', layout='wide')

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


def top_delivers(df1, top_asc):
    """Esta função calcula os entregadores mais lentos de cada cidade e retorna um dataframe com os 10 entregadores mais lentos
    para cada uma das cidades"""
    df_aux = (df1.loc[:, ['Time_taken(min)', 'City', 'Delivery_person_ID']]
              .groupby(['City', 'Delivery_person_ID'])
              .mean()
              .sort_values(['City', 'Delivery_person_ID'], ascending=top_asc)
              .reset_index())

    df_aux_01 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux_02 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_aux_03 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)

    df2 = pd.concat([df_aux_01, df_aux_02, df_aux_03])

    return df2

# --------------------------- Início da estrutura lógica do código ---------------------------


# ---------------------------
# Import Dataset
# ---------------------------
df = pd.read_csv('train.csv')
# ---------------------------
# Limpando dados
# ---------------------------
df1 = clean_code(df)


# Visão Entregadores
st.header('Marketplace - Visão Entregadores')

# =====================================
# Barra Lateral
# =====================================

# Logo Cury Company da barra lateral
image_path = 'food_delivery.png'
image = Image.open(image_path)
# Markdown Slogan Cury Company
st.sidebar.image(image,  width=150)
st.sidebar.markdown('# Cury Company')
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
    'Quais condições de trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)
# Filtro condições climáticas
weather_condition = st.sidebar.multiselect(
    'Quais condições climáticas?',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms',
        'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms',
             'conditions Stormy', 'conditions Sunny', 'conditions Windy']
)
# Aplicação dos filtros de data e tráfego
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas = df1['Weatherconditions'].isin(weather_condition)
df1 = df1.loc[linhas_selecionadas, :]

# =====================================
# Layout no Streamlit
# =====================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # A maior idade dos entregadore
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
        with col2:
            # A menor  idade dos entregadore
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        with col3:
            # A melhor condição dos veículo
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Veículo', melhor_condicao)
        with col4:
            # A pior condição dos veículos
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Veículo', pior_condicao)
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Avaliação média por Entregador')
            df_avg_ratings_per_deliver = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                          .groupby('Delivery_person_ID')
                                          .mean().reset_index()
                                          .sort_values('Delivery_person_Ratings', ascending=False))
            st.dataframe(df_avg_ratings_per_deliver,
                         use_container_width=True, height=500)
        with col2:
            st.markdown('##### Avaliação média por Trânsito')
            avg_std_rating_by_traffic = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                         .groupby('Road_traffic_density')
                                         .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            # mudança nome de colunas
            avg_std_rating_by_traffic.columns = [
                'devlivery_mean', 'delivery_std']
            # reset de index
            avg_std_rating_by_traffic = avg_std_rating_by_traffic.reset_index()
            st.dataframe(avg_std_rating_by_traffic, use_container_width=True)

            st.markdown('##### Avaliação média por Clima')
            avg_std_rating_by_weather = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                         .groupby('Weatherconditions')
                                         .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            # mudança nome de colunas
            avg_std_rating_by_weather.columns = ['weather_mean', 'weather_std']
            # reset do index
            avg_std_rating_by_weather = avg_std_rating_by_weather.reset_index()

            st.dataframe(avg_std_rating_by_weather, use_container_width=True)
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Top entregadores mais rápidos')
            df2 = top_delivers(df1, top_asc=True)
            st.dataframe(df2, use_container_width=True, height=500)
        with col2:
            st.subheader('Top Entregadores mais lentos')
            df2 = top_delivers(df1, top_asc=False)
            st.dataframe(df2, use_container_width=True, height=500)
