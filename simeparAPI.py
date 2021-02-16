import re
import json
import js2xml
import requests
import datetime
from slugify import slugify
from itertools import repeat
from bs4 import BeautifulSoup


class SimeparAPI:
    def __init__(self, municipio):
        if not municipio:
            raise Exception(
                "É preciso informar um código IBGE de município do Paraná")

        self.municipio = str(municipio)
        self.url = "http://www.simepar.br/prognozweb/simepar/forecast_by_counties/"
        self.buscaPagina()
        self.processaPagina()

    def buscaPagina(self):
        pagina = requests.get(self.url + self.municipio)
        self.pagina = pagina.text

    def processaPagina(self):
        soup = BeautifulSoup(self.pagina, "html5lib")

        dados_javascript = soup.find_all('script', {'type': 'text/javascript'})
        dados_para_buscar = dados_javascript[-1].text
        expressao_buscar = re.compile(r"var info = (.*);")
        retorno_buscar = json.loads(
            expressao_buscar.search(dados_para_buscar).group(1))

        dados_do_grafico = dados_javascript[-6].text
        parsed = js2xml.parse(dados_do_grafico)
        data = [d.xpath(".//array/number/@value")
                for d in parsed.xpath("//property[@name='data']")]
        categories = parsed.xpath(
            "//property[@name='categories']//string/text()")
        output = list(zip(repeat(categories), data))
        previsao_saida = {}

        for indice, data_previsao in enumerate(output[0][0][:15]):
            previsao_saida[data_previsao] = {
                'maxima': output[0][1][indice], 'minimo': output[1][1][indice]}

        dados_horaria_saida = {}
        dados_horaria_saida['dados'] = retorno_buscar
        dados_horaria_saida['previsao_hora'] = {}
        dados_horaria_saida['previsao'] = previsao_saida

        for dados_container in soup.find_all('div', {'class': 'wrapper'}):
            dados_data_extracao = dados_container.find(
                'div', {'class': 'currentDay'})
            temperatura = dados_container.find(
                'span', {'class': 'currentTemp'})
            data_extracao = [parte.strip()
                             for parte in dados_data_extracao.text.split('-')]
            temperatura_extracao = temperatura.text.strip()

            dados_extracao = dados_container.find(
                'div', {'id': 'collapseAcci'})
            dados_gerais = [' '.join(info.text.split())
                            for info in dados_extracao.find_all('span')]

            dados_previsao_horaria_extracao = dados_container.find(
                'div', {'id': 'accordion-hourly-wrapper'})

            dados_horaria = dados_previsao_horaria_extracao.find_all(
                'a', {'class': 'list_toggle'})

            for info in dados_horaria:
                dados_adicionais = {}
                hora = info.find('div', {'class': 'ah-time'}).text.strip()
                dados_temperatura = info.find(
                    'div', {'class': 'ah-temp'})
                temperatura = dados_temperatura.text.strip()
                tempo = dados_temperatura.find(
                    'i')['title'].strip()
                precipitacao = info.find(
                    'div', {'class': 'ah-prec'}).text.strip()
                vento = info.find('div', {'class': 'ah-wind'}).text.strip()

                dados_adicionais['temperatura'] = temperatura
                dados_adicionais['tempo'] = tempo
                dados_adicionais['chuva'] = precipitacao
                dados_adicionais['vento'] = vento
                dados_horaria_saida['previsao_hora'][hora] = dados_adicionais

                dados_gerais_horaria = dados_previsao_horaria_extracao.find_all(
                    'div', {'class': ['collapse', 'ah-body']})

                dados_gerais_horaria_saida = {}
                for info in dados_gerais_horaria:
                    dados = [' '.join(saida.text.split())
                             for saida in info.find_all('span')]
                    chunks = [dados[i:i+2] for i in range(0, len(dados), 2)]
                    for (nome, informacao) in chunks:
                        dados_gerais_horaria_saida[slugify(nome)] = informacao
                    dados_horaria_saida['previsao_hora'][hora].update(
                        dados_gerais_horaria_saida)
            self.dados_horario = dados_horaria_saida
