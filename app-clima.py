import pandas as pd
import streamlit as st
import requests
from io import BytesIO
from datetime import datetime, timedelta

# URL da logo do LAMMA para cabeçalho do app
LOGO_LAMMA_URL_HEADER = "https://lamma.com.br/wp-content/uploads/2024/08/lammapy-removebg-preview.png"

# URL da imagem do NASA POWER para a barra lateral
LOGO_NASA_POWER_URL_SIDEBAR = "https://www.earthdata.nasa.gov/s3fs-public/styles/small_third_320px_/public/2022-11/power_logo_event.png?VersionId=pZIOrAAZH6vCGOJMjhhwP91WJkg0sCus&itok=DrjfYom6"

# Função para buscar dados da API NASA POWER
def obter_dados_nasa(latitude, longitude, data_inicio, data_fim):
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR,RH2M,T2M,T2M_MAX,T2M_MIN,T2MDEW,WS2M,WS2M_MAX,WS2M_MIN,ALLSKY_SFC_SW_DWN,CLRSKY_SFC_SW_DWN&community=RE&longitude={longitude}&latitude={latitude}&start={data_inicio}&end={data_fim}&format=JSON"
    
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()
        # Organizando os dados que vêm da API
        parametros = dados['properties']['parameter']
        df = pd.DataFrame({
            'Data': list(parametros['T2M'].keys()),
            'P': parametros['PRECTOTCORR'].values(),  # Precipitação
            'UR': parametros['RH2M'].values(),        # Umidade Relativa
            'Tmed': parametros['T2M'].values(),       # Temperatura Média
            'Tmax': parametros['T2M_MAX'].values(),   # Temperatura Máxima
            'Tmin': parametros['T2M_MIN'].values(),   # Temperatura Mínima
            'Tdew': parametros['T2MDEW'].values(),    # Ponto de Orvalho
            'U2': parametros['WS2M'].values(),        # Velocidade do Vento a 2m
            'U2max': parametros['WS2M_MAX'].values(), # Velocidade Máxima do Vento a 2m
            'U2min': parametros['WS2M_MIN'].values(), # Velocidade Mínima do Vento a 2m
            'Qg': parametros['ALLSKY_SFC_SW_DWN'].values(), # Radiação Solar Incidente
            'Qo': parametros['CLRSKY_SFC_SW_DWN'].values()  # Radiação Solar na Superfície
        })
        return df
    else:
        return None

# Função para criar a planilha com as descrições das variáveis
def criar_planilha_descricoes():
    descricoes = {
        "Variável": ["P", "UR", "Tmed", "Tmax", "Tmin", "Tdew", "U2", "U2max", "U2min", "Qg", "Qo"],
        "Descrição": [
            "Precipitação acumulada (mm)",
            "Umidade relativa ao nível de 2 metros (%)",
            "Temperatura média diária (°C)",
            "Temperatura máxima diária (°C)",
            "Temperatura mínima diária (°C)",
            "Temperatura do ponto de orvalho ao nível de 2 metros (°C)",
            "Velocidade média do vento a 2 metros (m/s)",
            "Velocidade máxima do vento a 2 metros (m/s)",
            "Velocidade mínima do vento a 2 metros (m/s)",
            "Radiação solar incidente na superfície terrestre (W/m²)",
            "Radiação solar em condições de céu claro (W/m²)"
        ]
    }
    df_descricoes = pd.DataFrame(descricoes)
    return df_descricoes

# Função para obter a localização atual do usuário via IP (usando ipinfo.io)
def obter_localizacao_ip():
    url = "https://ipinfo.io"
    response = requests.get(url)
    if response.status_code == 200:
        location_data = response.json()
        latitude, longitude = map(float, location_data['loc'].split(','))
        return latitude, longitude
    else:
        st.error(f"Erro ao obter a localização: {response.status_code}")
        return None, None

# Interface do Streamlit
# Adiciona a logo do LAMMA no topo do app
st.image(LOGO_LAMMA_URL_HEADER, use_column_width=True)

st.title("NASA POWER - Download de Dados Climáticos")

# Botão para obter localização atual (posicionado antes dos inputs de latitude e longitude)
if st.button("Usar localização atual"):
    lat_atual, lon_atual = obter_localizacao_ip()
    if lat_atual and lon_atual:
        st.session_state['latitude'] = lat_atual
        st.session_state['longitude'] = lon_atual

# Input para latitude e longitude com valores atualizados após o uso da localização atual
latitude = st.number_input("Latitude", format="%.6f", value=st.session_state.get('latitude', -21.7946))
longitude = st.number_input("Longitude", format="%.6f", value=st.session_state.get('longitude', -48.1766))

# Definindo o intervalo de datas: máximo de 30 anos atrás e a data de fim como a data atual
hoje = datetime.today()
trinta_anos_atras = hoje - timedelta(days=30 * 365)

data_inicio = st.date_input("Data de início", value=trinta_anos_atras, min_value=datetime(1990, 1, 1), max_value=hoje)
data_fim = st.date_input("Data de fim", value=hoje, min_value=data_inicio, max_value=hoje)

# Converter as datas para o formato YYYYMMDD exigido pela API
data_inicio_formatada = data_inicio.strftime("%Y%m%d")
data_fim_formatada = data_fim.strftime("%Y%m%d")

# Botão para executar a busca
if st.button("Buscar dados"):
    # Chama a função para obter os dados
    dados = obter_dados_nasa(latitude, longitude, data_inicio_formatada, data_fim_formatada)
    df_descricoes = criar_planilha_descricoes()
    
    if dados is not None:
        # Exibe os dados na tabela
        st.write(dados)
        
        # Opção para download dos dados e da planilha de descrições em Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            dados.to_excel(writer, sheet_name="Dados_Climaticos", index=False)
            df_descricoes.to_excel(writer, sheet_name="Descrições", index=False)
        output.seek(0)
        
        st.download_button(label="Baixar em Excel", data=output, file_name="dados_climaticos_com_descricoes.xlsx")
    else:
        st.error("Erro ao buscar dados da NASA POWER")
