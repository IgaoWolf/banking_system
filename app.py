from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import mysql.connector
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Substitua pelo seu segredo

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
            session['conta'] = conta
            return redirect(url_for('get_balance', conta=conta))
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    return render_template('login.html')

@app.route('/create_account', methods=['POST'])
def create_account():
    try:
        data = request.json
        cpf = data['cpf']
        nome = data['nome']
        sobrenome = data['sobrenome']
        email = data['email']
        telefone = data['telefone']
        senha = data['senha']
        conta = generate_account_number()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO usuarios (conta, cpf, nome, sobrenome, email, telefone, senha) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (conta, cpf, nome, sobrenome, email, telefone, senha)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Account created successfully', 'conta': conta}), 201
    except KeyError as e:
        return jsonify({'error': f'Missing data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        conta = session.get('conta')
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
        conta_origem = session.get('conta')  # Obter a conta de origem da sessão do usuário logado
        conta_destino = request.form['conta_destino']
        valor = float(request.form['valor'])
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar se a conta de origem existe
        cursor.execute('SELECT saldo FROM contas WHERE conta = %s', (conta_origem,))
        saldo_origem = cursor.fetchone()
        print(f"Conta de origem: {conta_origem}, Saldo: {saldo_origem}")

        if not saldo_origem:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Origin account not found'}), 400

        # Verificar se a conta de destino existe
        cursor.execute('SELECT saldo FROM contas WHERE conta = %s', (conta_destino,))
        saldo_destino = cursor.fetchone()
        print(f"Conta de destino: {conta_destino}, Saldo: {saldo_destino}")

        if not saldo_destino:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Destination account not found'}), 400

        # Verificar saldo suficiente para a transferência
        if saldo_origem['saldo'] >= valor:
            cursor.execute('UPDATE contas SET saldo = saldo - %s WHERE conta = %s', (valor, conta_origem))
            cursor.execute('UPDATE contas SET saldo = saldo + %s WHERE conta = %s', (valor, conta_destino))
            conn.commit()

            # Obter o novo saldo da conta de origem
            cursor.execute('SELECT saldo FROM contas WHERE conta = %s', (conta_origem,))
            novo_saldo_origem = cursor.fetchone()
            print(f"Novo saldo da conta de origem ({conta_origem}): {novo_saldo_origem}")

            cursor.close()
            conn.close()

            return jsonify({
                'message': 'Transfer successful',
                'novo_saldo': novo_saldo_origem['saldo']
            }), 200
        else:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Insufficient funds'}), 400
    return render_template('transfer.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
