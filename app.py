from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta


DATABASE = 'checklist.db' 
def get_db_connection():
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():

    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                dia TEXT NOT NULL, -- Armazenado como TEXT no formato YYYY-MM-DD
                horario TEXT NOT NULL, -- Armazenado como TEXT no formato HH:MM:SS
                completa INTEGER NOT NULL DEFAULT 0 -- 0 para False, 1 para True
            )
        ''')
        db.commit()
        print("Tabela 'tarefas' criada ou já existente no SQLite.")

app = Flask(__name__)
CORS(app)

@app.route('/tarefas', methods=['GET'])
def get_tarefas():
    
    tarefas = []
    try:
        with get_db_connection() as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM tarefas ORDER BY dia, horario")
            tarefas_raw = cursor.fetchall()

            for tarefa_row in tarefas_raw:
                tarefa = dict(tarefa_row) 
                tarefa['completa'] = bool(tarefa['completa']) 
                tarefas.append(tarefa)
    except Exception as e:
        print(f"Erro ao buscar tarefas: {e}")
        return jsonify({"erro": "Erro interno ao buscar tarefas"}), 500
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
        datetime.strptime(dia_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"erro": "Formato de data inválido. Use 'YYYY-MM-DD'."}), 400

    try:
        with get_db_connection() as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO tarefas (titulo, dia, horario, completa) VALUES (?, ?, ?, ?)",
                (titulo, dia_str, horario, 0)
            )
            db.commit()

            return jsonify({
                "mensagem": "Tarefa adicionada com sucesso",
                "id": cursor.lastrowid
            }), 201
    except Exception as e:
        print(f"Erro ao adicionar tarefa: {e}")
        return jsonify({"erro": f"Erro ao adicionar tarefa: {e}"}), 500

@app.route('/tarefas/<int:tarefa_id>', methods=['PUT'])
def update_tarefa(tarefa_id):

    dados = request.get_json()
    completa = dados.get('completa')

    if completa is None:
        return jsonify({"erro": "O status 'completa' é obrigatório"}), 400
    
    completa_int = 1 if completa else 0

    try:
        with get_db_connection() as db:
            cursor = db.cursor()
            cursor.execute(
                "UPDATE tarefas SET completa = ? WHERE id = ?",
                (completa_int, tarefa_id)
            )
            db.commit()
            if cursor.rowcount == 0:
                return jsonify({"erro": "Tarefa não encontrada"}), 404
            return jsonify({"mensagem": f"Tarefa {tarefa_id} atualizada com sucesso"})
    except Exception as e:
        print(f"Erro ao atualizar tarefa: {e}")
        return jsonify({"erro": f"Erro ao atualizar tarefa: {e}"}), 500

@app.route('/tarefas/<int:tarefa_id>', methods=['DELETE'])
def delete_tarefa(tarefa_id):

    try:
        with get_db_connection() as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
            db.commit()
            if cursor.rowcount == 0:
                return jsonify({"erro": "Tarefa não encontrada"}), 404
            return jsonify({"mensagem": f"Tarefa {tarefa_id} excluída com sucesso"})
    except Exception as e:
        print(f"Erro ao deletar tarefa: {e}")
        return jsonify({"erro": f"Erro ao deletar tarefa: {e}"}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
