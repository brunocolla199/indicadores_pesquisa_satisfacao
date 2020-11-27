#Tratar dados
import pandas as pd
import numpy as np

#Outros
import json, requests, base64
from io import StringIO
from datetime import date, datetime
from seaborn.palettes import color_palette
import six, os
from pathlib import Path

#Flask
from flask import Flask, request, render_template, url_for
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api

#Gráficos
import seaborn as sns
sns.set_theme(style="ticks", color_codes=True)
import matplotlib.pyplot as plt

#Third party
from env import flask

app = Flask(__name__, template_folder='templates')
api = Api(app)
CORS(app)

#Receber a requisição inicial
@app.route('/graficos', methods=['GET'])
def getting_data_ged():


    ## MINHAS REQUISIÇÕES PARA TESTAR
    body = { 
                "listaIdArea": [
                        "9a41c6e7-32c1-4d80-b6c0-21a07e971ada",
                        "2b01d741-822e-45a4-94a9-65360ac8dca1",
                        "82f2cea4-99bc-46ad-9a8d-b9c837a08b79",
                        "f8779fc0-afae-4ce9-9c9e-a7779496d82e",
                        "3c92bef0-7a67-4779-97f3-a6ab7a1e3bef",
                        "f4374f19-f0ad-461a-af25-209ccb105384",
                        "ed74e020-f7c3-447c-ae96-79c3d2cb711c",
                        "f60b3c7e-788f-4c3b-8622-1d11a9521262",
                        "6ce63d3f-7de6-47ed-836d-a81a02e665e3",
                        "03e2adf7-01d5-46fd-aea4-6971582ef0b7",
                        "4c031f4d-9f27-4a3c-8d91-17995abb99c6",
                        "dd752d9f-d936-43a0-82dc-b8013d3eff80",
                        "0f7049b8-32bb-41f8-8048-4e454505519d",
                        "e8015d08-e15a-4483-b163-59d942511360",
                        "04e6f780-de8d-47a0-8fa8-272b3b8f380d",
                        "720dfaee-6ba4-4a77-aa40-11327acdf36c",
                        "991b9666-c292-46a6-8fb0-6f0b8e451b65",
                        "e582aed5-ae85-45ca-8300-8f12dd15a1ae",
                        "21b64383-5430-40a9-9627-0095f0a34144",
                        "7577a987-1370-4d0a-8be2-47d2cae8d6d2",
                        "38bf37c8-d099-42e0-b9bc-3a6e95a92528",
                        "994ea197-fb92-4d69-a4ca-a238483a750f",
                        "c997893b-251d-4622-afc2-4a1c5f3ddea3"
                ],
                "listaIndice": [
                ],
                "inicio": 0,
                "fim": 1000
            }  

    headers = {'Cookie' : "CXSSID=Mnw6fGFkbXw6fC0xfDp8MTg0ZmE1OTdmMjk1YmUyY2RmODIwY2NkZTZkN2E1YmZ8Onw3NWZiZmI5MmMxYzI2ZDdiM2FmM2QzNzAwOWY2MzY4NDhkNWRiM2E2",
            'content-type' : 'application/json'
            }

    url = "http://127.0.0.1:8080/speed/rest/registro/pesquisa"

    params = {
        'url' : url,
        'body' : body,
        'type_view' : request.args.get('tipo')
    }

    ## USAR PARA A APLICAÇÃO DO CRIXIN

    # params = {
    #     'url' : '{}/registro/pesquisa'.format(request.args.get('url')),
    #     'type_view' : request.args.get('tipo'),
    #     'token' : request.args.get('token'),
    #     'body' : json.loads(request.args.get('body'))
    # }

    # headers = {'Cookie' : 'CXSSID=' + params['token'],
    #         'content-type' : 'application/json'
    #         }


    return get_data_ged(params, headers)

#Buscar dados do GED
def get_data_ged(params, headers):

    body = json.dumps(params['body'], ensure_ascii=False)
    response_get = requests.post(params['url'], headers=headers, data=body)
    return preparing_dataframe(response_get.content, params['type_view'], headers)

#Crio um dataframe baseado nos dados recebidos
def preparing_dataframe(data, type_view, headers):
    
    data = json.loads(data.decode('utf-8'))
    dataframe = pd.DataFrame(columns=['IdArea','Processo', 'Descrição', 'Status', 'Área', 'Abrangência', 'Data de emissão', 'Data de validade', 'Data de aviso', 'Observação', 'Cópia', 'Dias antecedência'])
    for i in data['listaRegistro']:
        chave_valor = {}
        data = json.dumps(i)
        for indice in i['listaIndice']:
            chave_valor[indice['identificador'].strip().upper()] = indice['valor']
        dataframe = dataframe.append({
            'IdArea'            : get_area_name(i['idArea'], headers),
            'Processo'          : chave_valor['PROCESSO'],
            'Descrição'         : chave_valor['DESCRICAO'],
            'Status'            : chave_valor['STATUS'],
            'Área'              : chave_valor['RESPONSÁVEL'],
            'Abrangência'       : chave_valor['ABRANGENCIA'],
            'Data de emissão'   : chave_valor['EMISSAO'],
            'Data de validade'  : chave_valor['VALIDADE'],
            'Data de aviso'     : chave_valor['DATA_VALIDADA'],
            'Observação'        : chave_valor['OBSERVACAO'],
            'Cópia'             : chave_valor['COPIA CONTROLADA'],
            'Dias antecedência' : chave_valor['DIAS_ANTECEDENCIA']                    
        }, ignore_index=True)
    return roteador(dataframe, type_view)

#Licenças vigentes e vencidas por órgão interveniente
def roteador(data, type_view):

    if type_view == 'vencidas':
        return vencidas_vigentes_por_orgao(data)
    elif type_view == 'vencerao':
        return vencerao_3_meses(data)


def vencidas_vigentes_por_orgao(dataframe):

    today = date.today().strftime("%d/%m/%Y")
    today = pd.to_datetime(today, format="%d/%m/%Y")
    subset_vencidas_vigentes = dataframe
    subset_vencidas_vigentes = subset_vencidas_vigentes.sort_values(by=['IdArea'], ascending=True)
    #subset_vencidas_vigentes['Vencida'] = subset_vencidas_vigentes['Data de validade'].apply(lambda x: 'Indefinida' if x == None else ('Sim' if pd.to_datetime(x, format='%d/%m/%Y') < today else 'Não'))
    
    status_order = ['Vigente', 'Em renovação', 'Não Vigente', 'Processo suspenso']

    plot = sns.catplot(y="IdArea", kind="count",
            palette="pastel",col="Status", edgecolor=".6",
            data=subset_vencidas_vigentes, col_order=status_order)
    plt.subplots_adjust(top=1.5)
    #plot.fig.suptitle('Licenças vigentes e vencidas por órgão interveniente')
    plot.set_xlabels('Quantidade')
    plot.set_ylabels('Órgão')

    ##VERIFICAR, POIS NO SERVIDOR DA DP DEU PAU!
    img_location = Path(__file__).absolute().parent
    file_location = img_location / 'static/my_plot.png' 
    plot.savefig(file_location)

    #Base64 na imagem pra enviar
    with open(file_location, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    json_dumped = json.dumps({'base64' : encoded_string.decode('utf-8')})

    return json_dumped

def vencerao_3_meses(dataframe):
    
    #BUSCAR O DIA DE HOJE FORMATADO
    today = date.today().strftime("%d/%m/%Y")
    today = pd.to_datetime(today, format="%d/%m/%Y")
    
    #SUBSET DATAFRAME ORIGINAL
    subset_vencera = dataframe
    
    #DATAFRAME PARA MOSTRAR PARA O CLIENTE
    columns = ['Órgão','Área','Descrição', 'Vencerá em dias']
    dataframe_vencera = pd.DataFrame(columns=columns)
    

    #Transformação e cálculo para saber quantos dias faltam
    for i in subset_vencera.iterrows():
        data_validade = i[1]['Data de validade']
        nome_area = i[1]['IdArea']
        area_responsavel = i[1]['Área']
        descricao = i[1]['Descrição']
        
        if data_validade != None:
            converter_to_data = pd.to_datetime(data_validade, format='%d/%m/%Y')
            date_diff = (converter_to_data - today)       
            #Vencer entre 90 a 0 dias
            if((date_diff <= pd.Timedelta(90, unit='days')) & (date_diff >= pd.Timedelta(0, unit='days'))):
                #Tratar a diferença dos dados
                date_diff = str(date_diff)
                date_diff = date_diff.replace(' days', '')
                date_diff = date_diff.replace('00:00:00', '')
                date_diff = int(date_diff)
                
                
                dataframe_vencera = dataframe_vencera.append({'Órgão' : nome_area,'Área' : area_responsavel, 'Descrição' : descricao, 'Vencerá em dias' : date_diff}, ignore_index=True)
                dataframe_vencera = dataframe_vencera.sort_values(by=['Vencerá em dias']) 
    
    df_to_table = render_mpl_table(dataframe_vencera)
    fig = df_to_table.get_figure()

    ##VERIFICAR, POIS NO SERVIDOR DA DP DEU PAU!
    img_location = Path(__file__).absolute().parent
    file_location = img_location / 'static/dataframe_vencera.png' 
    fig.savefig(file_location)
    
    #Base64 na imagem pra enviar
    with open(file_location, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    json_dumped = json.dumps({'base64' : encoded_string.decode('utf-8')})
    return json_dumped
    

#Transformar dataframe em imagem
def render_mpl_table(data, col_width=11, row_height=0.625, font_size=14,
                    header_color='#1e88e5', row_colors=['#f1f1f2', 'w'], edge_color='w',
                    bbox=[0, 0, 1, 1], header_columns=0,
                    ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=(45,10))
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax

#Buscar nome da área
def get_area_name(area,headers):

    url = 'http://localhost:8080/speed/rest/area/{}/nome'.format(area)
    response_get_area_name = requests.get(url, headers=headers)
    name_area = response_get_area_name.content.decode('utf-8')
    return name_area 

if __name__ == "__main__":
    app.run(host='0.0.0.0')

