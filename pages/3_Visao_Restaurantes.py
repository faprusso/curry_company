import pandas as pd
import folium
import plotly_express as px
from haversine import haversine
import streamlit as st
from PIL import Image
import datetime
from streamlit_folium import folium_static
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽️', layout='wide')

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


def distance(df1, fig):
    """Esta função calcula a distância média dos restaurantes e os locais de entrega"""
    if fig == False:
        # Calculo da distância entre o restaurante e local de entrega para cada pedido
        cols = ['Restaurant_latitude', 'Restaurant_longitude',
                'Delivery_location_latitude', 'Delivery_location_longitude']

        # Criando a coluna que vai armazenar cada uma das distâncias entre o restaurante e o local de entrega
        df1['distance'] = (df1.loc[:, cols]
                           .apply(lambda x: haversine(
                               (x['Restaurant_latitude'],
                                x['Restaurant_longitude']),
                               (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))

        average_distance = np.round(df1['distance'].mean(), 2)
        return average_distance
    else:
        # Calculo da distância entre o restaurante e local de entrega para cada pedido
        cols = ['Restaurant_latitude', 'Restaurant_longitude',
                'Delivery_location_latitude', 'Delivery_location_longitude']

        # Criando a coluna que vai armazenar cada uma das distâncias entre o restaurante e o local de entrega
        df1['distance'] = (df1.loc[:, cols]
                           .apply(lambda x: haversine(
                               (x['Restaurant_latitude'],
                                x['Restaurant_longitude']),
                               (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))

        average_distance = df1.loc[:, ['City', 'distance']].groupby(
            'City').mean().reset_index()

        fig = go.Figure(data=[go.Pie(labels=average_distance['City'],
                                     values=average_distance['distance'], pull=[0, 0.1, 0])])

        return fig


def avg_std_time_delivery(df1, festival, op):
    """Esta função calcula o tempo médio e o desvio padrão deo tempo de entrega.
    Parâmetros:
        Input: 
            - df: Dataframe com os dados necessários para o cálculo
            - op: Tipo de operação que precisa ser calculado:
                - 'avg_time': calcula o tempo médio
                - 'std_time': calcula o desvio padrão do tempo    
        Output:
            - df: Dataframe com 2 colunas e 1 linhas
    """
    df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
              .groupby('Festival')
              .agg({'Time_taken(min)': ['mean', 'std']}))

    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()

    df_aux = np.round(
        df_aux.loc[df_aux['Festival'] == festival, op], 2)
    return df_aux


def avg_std_time_graph(df1):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby(
        'City').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(
        type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')

    return fig


def avg_std_time_on_traffic(df1):
    df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(
        ['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig


# ---------------------------
# Import Dataset
# ---------------------------
df = pd.read_csv('train.csv')
# ---------------------------
# Limpando dados
# ---------------------------
df1 = clean_code(df)


# Visão Restaurantes
st.header('Marketplace - Visão Restaurantes')

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

        col1, col2 = st.columns(2, gap='small')

        with col1:
            delivery_unique = df1['Delivery_person_ID'].nunique()
            col1.metric('Entregadores únicos', delivery_unique)
        with col2:
            average_distance = distance(df1, fig=False)
            col2.metric('Distância média', average_distance)

    with st.container():
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col1.metric('Tempo Médio entrega c/ Fest', df_aux)
        with col2:
            df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
            col2.metric('Tempo médio entrega s/ Fest', df_aux)
        with col3:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
            col3.metric('STD entrega c/ Fest', df_aux)
        with col4:
            df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
            col4.metric('STD entrega s/ Fest', df_aux)
    with st.container():
        st.markdown("""---""")
        st.title('Tempo Médio de Entrega por Cidade')
        fig = avg_std_time_graph(df1)
        st.plotly_chart(fig)

    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do tempo')

        col1, col2 = st.columns(2)

        with col1:
            fig = distance(df1, fig=True)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("""---""")
        st.title('Distribuição da Distância')

        df_aux = (df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']]
                  .groupby(['City', 'Type_of_order'])
                  .agg({'Time_taken(min)': ['mean', 'std']}))
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()

        st.dataframe(df_aux, height=460)
