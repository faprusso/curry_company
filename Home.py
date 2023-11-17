import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🍔'
)


image = Image.open('food_delivery.png')
st.sidebar.image(image, width=150)

st.sidebar.markdown(Cury Company)
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Cury Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar este Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Méticas gerais de comportamento;
        - Visão Tática: Indicadores semanais de crescimento;
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Email: faprusso@gmail.com
"""
)
