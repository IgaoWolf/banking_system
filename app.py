from flask import Flask, request, jsonify
import mysql.connector
import random
import string

app = Flask(__name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='bank',
        password='passwdbank',
        database='banking'
    )
    return conn

def generate_account_number():
    return ''.join(random.choices(string.digits, k=10))

@app.route('/login', methods=['POST'])
def login():
    conta = request.json['conta']
    senha = request.json['senha']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuarios WHERE conta = %s AND senha = %s', (conta, senha))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return jsonify(user)
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/create_account', methods=['POST'])
def create_account():
    cpf = request.json['cpf']
    nome = request.json['nome']
    sobrenome = request.json['sobrenome']
    email = request.json['email']
    telefone = request.json['telefone']
    senha = request.json['senha']
    conta = generate_account_number()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO usuarios (cpf, nome, sobrenome, email, telefone, senha, conta) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (cpf, nome, sobrenome, email, telefone, senha, conta)
    )
    cursor.execute(
        'INSERT INTO contas (conta, saldo, usuario_id) VALUES (%s, %s, %s)',
        (conta, 0.00, cursor.lastrowid)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Account created successfully', 'conta': conta}), 201

@app.route('/balance', methods=['GET'])
def get_balance():
    conta = request.args.get('conta')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT saldo FROM contas WHERE conta = %s', (conta,))
    balance = cursor.fetchone()
    cursor.close()
    conn.close()
    if balance:
        return jsonify(balance)
    else:
        return jsonify({'error': 'Account not found'}), 404

@app.route('/withdraw', methods=['POST'])
def withdraw():
    conta = request.json['conta']
    valor = request.json['valor']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT saldo FROM contas WHERE conta = %s', (conta,))
    saldo_atual = cursor.fetchone()
    
    if saldo_atual and saldo_atual['saldo'] >= valor:
        cursor.execute('UPDATE contas SET saldo = saldo - %s WHERE conta = %s', (valor, conta))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Withdrawal successful'}), 200
    else:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Insufficient funds or account not found'}), 400

@app.route('/transfer', methods=['POST'])
def transfer():
    conta_origem = request.json['conta_origem']
    conta_destino = request.json['conta_destino']
    valor = request.json['valor']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT saldo FROM contas WHERE conta = %s', (conta_origem,))
    saldo_origem = cursor.fetchone()
    
    cursor.execute('SELECT saldo FROM contas WHERE conta = %s', (conta_destino,))
    saldo_destino = cursor.fetchone()
    
    if saldo_origem and saldo_destino and saldo_origem['saldo'] >= valor:
        cursor.execute('UPDATE contas SET saldo = saldo - %s WHERE conta = %s', (valor, conta_origem))
        cursor.execute('UPDATE contas SET saldo = saldo + %s WHERE conta = %s', (valor, conta_destino))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Transfer successful'}), 200
    else:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Insufficient funds or accounts not found'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
