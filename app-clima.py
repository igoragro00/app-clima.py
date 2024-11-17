import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

# Função para calcular o PMI (Percentual de Maturação do Amendoim)
def calcular_pmi(white, yellow1, yellow2, orange, brown, black):
    total_pods = white + yellow1 + yellow2 + orange + brown + black
    mature_pods = orange + brown + black
    if total_pods > 0:
        return mature_pods / total_pods * 100
    else:
        return None

# Função para gerar o PDF com as informações das amostras e a recomendação de colheita
def gerar_pdf(dados, grafico_path, pmi_medio, pmi_medio_cor, cultivar_selecionada, recomendacao):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)

    # Centralizando o cabeçalho do PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(A4[0] / 2, 800, "Relatório de Maturação do Amendoim")
    
    # Data de exportação com menor espaçamento
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(A4[0] / 2, 780, f"Data da Exportação: {datetime.now().strftime('%Y-%m-%d')}")

    c.setFont("Helvetica", 12)
    y = 740  # Ajustando o ponto inicial para texto das amostras

    # Adicionando as amostras em uma única coluna, incluindo o nome da cultivar
    for i, (cultivar, info) in enumerate(dados.items()):
        c.drawString(50, y, f'Amostra {i+1} - Cultivar {cultivar_selecionada}: Amostra {i+1}')
        c.drawString(50, y - 15, f'PMI: {info["pmi"]:.2f}%')
        y -= 40

    y -= 20  # Ajusta a posição antes de exibir o PMI médio

    # Adicionar o PMI médio com cor vermelha ou verde em destaque
    c.setFillColor(pmi_medio_cor)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(A4[0] / 2, y, f'PMI Médio da Cultivar {cultivar_selecionada}: {pmi_medio:.2f}%')
    c.setFillColorRGB(0, 0, 0)  # Volta à cor preta para o restante do texto

    # Exibir a recomendação de colheita para o PMI médio
    y -= 20
    c.drawString(50, y, recomendacao)

    y -= 40  # Diminuindo o espaçamento para evitar sobreposição com o gráfico

    # Ajustar a posição e tamanho do gráfico mais abaixo no PDF para evitar sobreposição
    c.drawImage(grafico_path, 50, 50, width=450, height=250)

    # Adicionar legenda do gráfico abaixo do gráfico
    c.setFont("Helvetica", 10)
    c.drawString(50, 30, 'PMI >= 70% (Colheita Recomendável): Verde')
    c.drawString(50, 20, 'PMI < 70% (Aguarde a Colheita): Vermelho')

    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    return pdf_buffer

# Interface do Streamlit
st.title("Calculadora de Maturação do Amendoim")

# Adiciona a logo do LAMMA no cabeçalho do app
st.image("https://lamma.com.br/wp-content/uploads/2024/08/lammapy-removebg-preview.png", use_column_width=True)

# Informações sobre o laboratório
st.subheader("Calculadora desenvolvida pelo LAMMA - Laboratório de Máquinas e Mecanização Agrícola da UNESP/Jaboticabal")

# Adicionando informações na barra lateral
st.sidebar.title("Monitoramento da Maturação do Amendoim")

# Adicionando a imagem da tabela do PMI no início da barra lateral
st.sidebar.image("https://www.fca.unesp.br/Modulos/Noticias/2258/tabela-frente-jpg.jpg", caption='Tabela de Maturação do Amendoim (Fonte: UNESP)')

# Texto explicativo na barra lateral com linguagem didática
st.sidebar.write("""
Acompanhar o ponto de maturação do amendoim é essencial para garantir uma colheita eficiente e um produto de qualidade. 
O método "Hull Scrape" nos ajuda a determinar o momento certo para a colheita. Esse método pode ser feito de duas formas: lavando as vagens com um jato d'água ou, diretamente no campo, raspando a casca das vagens com um canivete. Ambas as técnicas revelam a cor interna da vagem, indicando o quão maduro o amendoim está.

Durante o processo, selecionamos plantas de uma área de 2m² e coletamos vagens completamente desenvolvidas. 
Ao raspar a casca das vagens, conseguimos ver cores que variam do branco (vagem ainda verde) até o preto (vagem madura). 
Essas cores são classificadas em seis grupos: branco, dois tons de amarelo, laranja, marrom e preto.
""")

st.sidebar.write("""
Para calcular o Índice de Maturação do Amendoim (PMI), observamos as vagens nas cores laranja, marrom e preto, que indicam que os amendoins estão prontos para a colheita. O PMI é calculado da seguinte forma:

*PMI = (Laranja + Marrom + Preto) / Total de Vagens x 100*

O ideal é iniciar a colheita quando pelo menos 70% das vagens estiverem nesses tons mais escuros. Assim, garantimos que a maioria dos amendoins esteja no ponto ideal de maturação, melhorando a qualidade do produto final e facilitando o armazenamento e processamento.
""")

st.sidebar.write("""
Utilize este método para monitorar a maturidade do seu amendoim e garantir o melhor resultado para a sua colheita!
""")

st.sidebar.write("""
**RESPONSÁVEIS:**  
- Prof. Dr. Rouverson Pereira da Silva – FCAV/UNESP [Linkedin](https://www.linkedin.com/in/rouverson-pereira-da-silva/)
- Msc. Igor Cristian de Oliveira Vieira - FCAV/UNESP [Linkedin](https://www.linkedin.com/in/eng-igor-vieira/)
""")

# Sidebar "REALIZAÇÃO"
st.sidebar.subheader("REALIZAÇÃO")
st.sidebar.image("http://lamma.com.br/wp-content/uploads/2024/02/IMG_1713-300x81.png")
st.sidebar.write("[Visite o site do LAMMA](https://lamma.com.br/)")
st.sidebar.write("[Visite o instagram do LAMMA](https://www.instagram.com/lamma.unesp/)")
st.sidebar.write("[Visite o site do RSRG](https://www.rsrg.net.br/)")

# Seleção de cultivares
cultivares = st.multiselect(
    "Selecione as cultivares para avaliação:",
    ["Granoleico", "IAC 503", "IAC 677", "IAC OL3"]
)

# Observação em vermelho sobre a quantidade de vagens necessárias
st.markdown("<p style='color:red;'>Deve-se selecionar de 180 a 200 vagens para cada amostra para o cálculo.</p>", unsafe_allow_html=True)

# Armazenamento dos dados de maturação para cada cultivar
dados_cultivares = {}

if len(cultivares) == 1:  # Permite selecionar até 10 amostras quando uma cultivar é escolhida
    st.markdown("<p style='color:red;'>Você pode selecionar até 10 amostras para essa cultivar.</p>", unsafe_allow_html=True)
    
    # Selecionar até 10 amostras
    num_amostras = st.slider("Número de amostras (até 10)", 1, 10, 1)
    amostras_dados = []

    cultivar_selecionada = cultivares[0]  # Pegar o nome da cultivar selecionada

    for i in range(num_amostras):
        st.subheader(f"Insira a quantidade de vagens para a amostra {i+1}")
        white = st.number_input(f"Branca - Amostra {i+1}:", min_value=0, value=0, step=1, key=f'white_{i}')
        yellow1 = st.number_input(f"Amarelo 1 - Amostra {i+1}:", min_value=0, value=0, step=1, key=f'yellow1_{i}')
        yellow2 = st.number_input(f"Amarelo 2 - Amostra {i+1}:", min_value=0, value=0, step=1, key=f'yellow2_{i}')
        orange = st.number_input(f"Laranja - Amostra {i+1}:", min_value=0, value=0, step=1, key=f'orange_{i}')
        brown = st.number_input(f"Marrom - Amostra {i+1}:", min_value=0, value=0, step=1, key=f'brown_{i}')
        black = st.number_input(f"Preto - Amostra {i+1}:", min_value=0, value=0, step=1, key=f'black_{i}')

        # Calcula o PMI para a amostra
        pmi = calcular_pmi(white, yellow1, yellow2, orange, brown, black)
        
        # Armazena os dados da amostra
        amostras_dados.append({
            'white': white,
            'yellow1': yellow1,
            'yellow2': yellow2,
            'orange': orange,
            'brown': brown,
            'black': black,
            'pmi': pmi
        })
    
    # Botão para calcular o PMI
    if st.button("Calcular PMI para as Amostras"):
        pmi_values = []
        for i, amostra in enumerate(amostras_dados):
            pmi = amostra['pmi']
            
            # Verificação e exibição de resultados
            if pmi is not None:
                st.write(f"PMI da Amostra {i+1}: {pmi:.2f}%")
                pmi_values.append(pmi)
                if pmi >= 70:
                    st.success(f"Recomendação para a Amostra {i+1}: Iniciar colheita mecanizada.")
                else:
                    st.info(f"Recomendação para a Amostra {i+1}: Ainda não é o momento ideal para a colheita.")

                # Visualização dos Dados para cada Amostra com fundo cinza apenas dentro do gráfico
                fig, ax = plt.subplots()
                ax.set_facecolor('lightgray')  # Apenas a parte interna do gráfico com fundo cinza
                cores = ['Branca', 'Amarelo 1', 'Amarelo 2', 'Laranja', 'Marrom', 'Preto']
                quantidades = [amostra['white'], amostra['yellow1'], amostra['yellow2'], amostra['orange'], amostra['brown'], amostra['black']]
                bars = ax.bar(cores, quantidades, color=['white', 'yellow', 'yellow', 'orange', 'brown', 'black'])
                ax.set_ylabel('Quantidade de Vagens')
                ax.set_title(f'Distribuição de Vagens por Cor - Amostra {i+1}')

                # Centralizar e adicionar rótulos às barras (mantendo os valores de % sem o símbolo)
                for bar in bars:
                    yval = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', ha='center', va='bottom')

                st.pyplot(fig)
            else:
                st.error(f"Erro: Por favor, insira valores válidos para todas as cores da Amostra {i+1}.")

        # Cálculo do PMI médio
        pmi_medio = sum(pmi_values) / len(pmi_values)
        if pmi_medio >= 70:
            cor_pmi_medio = 'green'
            recomendacao_medio = f"Recomendação para o PMI médio: Iniciar colheita mecanizada."
        else:
            cor_pmi_medio = 'red'
            recomendacao_medio = f"Recomendação para o PMI médio: Ainda não é o momento ideal para a colheita."

        st.markdown(f"<p style='color:{cor_pmi_medio};'>PMI Médio das Amostras: {pmi_medio:.2f}%</p>", unsafe_allow_html=True)
        st.write(recomendacao_medio)

        # Gráfico de Comparação de PMI entre Amostras com fundo cinza apenas na parte interna
        fig, ax = plt.subplots()
        ax.set_facecolor('lightgray')  # Fundo cinza apenas dentro do gráfico
        ax.bar(range(1, len(pmi_values) + 1), pmi_values, color=['green' if pmi >= 70 else 'red' for pmi in pmi_values])
        ax.set_title('Comparação de PMI entre Amostras')
        ax.set_xlabel('Amostra')
        ax.set_ylabel('PMI (%)')

        # Centralizar e adicionar rótulos às barras (mantendo o valor do PMI sem o símbolo de %)
        for i, bar in enumerate(ax.patches):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{bar.get_height():.2f}', ha='center', va='bottom')

        # Adicionar legenda abaixo do gráfico
        green_patch = plt.Line2D([0], [0], color='green', lw=4, label='PMI >= 70% (Colheita Recomendável)')
        red_patch = plt.Line2D([0], [0], color='red', lw=4, label='PMI < 70% (Aguarde a Colheita)')
        ax.legend(handles=[green_patch, red_patch], loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

        st.pyplot(fig)

        # Salva o gráfico como um arquivo temporário
        grafico_path = "grafico_comparacao_amostras.png"
        fig.savefig(grafico_path)

        # Botão para gerar e baixar o PDF
        pdf_output = gerar_pdf({f"Amostra {i+1}": amostra for i, amostra in enumerate(amostras_dados)}, grafico_path, pmi_medio, cor_pmi_medio, cultivar_selecionada, recomendacao_medio)
        st.download_button(label="Baixar Relatório PDF", 
                           data=pdf_output, 
                           file_name='relatorio_maturacao_amostras.pdf', 
                           mime='application/pdf')

        # Remove o arquivo temporário após o download
        if os.path.exists(grafico_path):
            os.remove(grafico_path)

#streamlit run "c:/Users/Igor Vieira/App_Lamma/app_lamma_Mat.py"

