from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

MONGO_URI = "mongodb+srv://augzto:Atkzz240@cluster0.njsipnc.mongodb.net/?retryWrites=true&w=majority" 
try:
    client = MongoClient(MONGO_URI)
    db = client["check_list_DB"]
    collection = db["tarefas"]
    print("Conectado ao MongoDB.")
except Exception as e:
    print(f"Erro ao conectar ao MongoDB: {e}")
    exit()

def init_db():
    pass

app = Flask(__name__)
CORS(app)

@app.route('/tarefas', methods=['GET'])
def get_tarefas():
    tarefas_cursor = collection.find().sort([('dia', 1), ('horario', 1)])
    tarefas = []
    for tarefa in tarefas_cursor:
        tarefa['_id'] = str(tarefa['_id'])
        tarefa['dia'] = tarefa['dia'].strftime('%Y-%m-%d')
        tarefas.append(tarefa)
    return jsonify(tarefas)

@app.route('/tarefas', methods=['POST'])
def add_tarefa():
    nova_tarefa = request.get_json()
    titulo = nova_tarefa.get('titulo')
    dia_str = nova_tarefa.get('dia')
    horario = nova_tarefa.get('horario')

    if not titulo or not dia_str or not horario:
        return jsonify({"erro": "Todos os campos (titulo, dia, horario) são obrigatórios"}), 400
    
    try:
        dia_obj = datetime.strptime(dia_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"erro": "Formato de data inválido. Use 'YYYY-MM-DD'."}), 400

    tarefa_doc = {
        'titulo': titulo,
        'dia': dia_obj,
        'horario': horario,
        'completa': False
    }

    try:
        result = collection.insert_one(tarefa_doc)
        return jsonify({
            "mensagem": "Tarefa adicionada com sucesso",
            "id": str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({"erro": f"Erro ao adicionar tarefa: {e}"}), 500

@app.route('/tarefas/<tarefa_id>', methods=['PUT'])
def update_tarefa(tarefa_id):
    dados = request.get_json()
    completa = dados.get('completa')

    if completa is None:
        return jsonify({"erro": "O status 'completa' é obrigatório"}), 400

    try:
        collection.update_one(
            {'_id': ObjectId(tarefa_id)},
            {'$set': {'completa': completa}}
        )
        return jsonify({"mensagem": f"Tarefa {tarefa_id} atualizada com sucesso"})
    except Exception as e:
        return jsonify({"erro": f"Erro ao atualizar tarefa: {e}"}), 500

@app.route('/tarefas/<tarefa_id>', methods=['DELETE'])
def delete_tarefa(tarefa_id):
    try:
        collection.delete_one({'_id': ObjectId(tarefa_id)})
        return jsonify({"mensagem": f"Tarefa {tarefa_id} excluída com sucesso"})
    except Exception as e:
        return jsonify({"erro": f"Erro ao deletar tarefa: {e}"}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)