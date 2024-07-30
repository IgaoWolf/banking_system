from flask import Flask, request, jsonify, render_template, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='bank',
        password='passwdbank',
        database='banking'
    )
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conta = request.form['conta']
        senha = request.form['senha']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuarios WHERE conta = %s AND senha = %s', (conta, senha))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return redirect(url_for('get_balance', conta=conta))
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    return render_template('login.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        cpf = request.form['cpf']
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        email = request.form['email']
        telefone = request.form['telefone']
        senha = request.form['senha']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO usuarios (cpf, nome, sobrenome, email, telefone, senha) VALUES (%s, %s, %s, %s, %s, %s)',
            (cpf, nome, sobrenome, email, telefone, senha)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Account created successfully'}), 201
    return render_template('create_account.html')

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
        return render_template('balance.html', balance=balance['saldo'])
    else:
        return jsonify({'error': 'Account not found'}), 404

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        conta = request.form['conta']
        valor = request.form['valor']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT saldo FROM contas WHERE conta = %s', (conta,))
        saldo_atual = cursor.fetchone()
        if saldo_atual and saldo_atual['saldo'] >= float(valor):
            cursor.execute('UPDATE contas SET saldo = saldo - %s WHERE conta = %s', (valor, conta))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Withdrawal successful'}), 200
        else:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Insufficient funds or account not found'}), 400
    return render_template('withdraw.html')

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        conta_origem = request.form['conta_origem']
        conta_destino = request.form['conta_destino']
        valor = request.form['valor']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT saldo FROM contas WHERE conta = %s', (conta_origem,))
        saldo_origem = cursor.fetchone()
        cursor.execute('SELECT saldo FROM contas WHERE conta = %s', (conta_destino,))
        saldo_destino = cursor.fetchone()
        if saldo_origem and saldo_destino and saldo_origem['saldo'] >= float(valor):
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
    return render_template('transfer.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
