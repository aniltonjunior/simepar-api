import flask
from flask import request, jsonify
from simeparAPI import SimeparAPI

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return '''<h1>SIMEPAR API</h1>
<p>Uma API protótipo para pesquisa de dados metereológicos da SIMEPAR</p>'''


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>O recurso não foi encontrado.</p>", 404


@app.route('/api/v1/resources/forecast', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')

    dados = SimeparAPI(id)

    return jsonify(dados.dados_horario)


app.run()
