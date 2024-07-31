from flask import Flask, request, render_template, redirect, jsonify, session, url_for
import mysql.connector
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='bank',
        password='passwdbank',
        database='banking'
    )
    return conn

def generate_account_number():
    return str(random.randint(1000000000, 9999999999))

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
            return redirect(url_for('get_balance'))  # Redirecionar para a página de saldo
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
        cursor.execute(
            'INSERT INTO contas (conta, saldo) VALUES (%s, %s)',
            (conta, 0)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Account created successfully', 'conta': conta}), 201
    except mysql.connector.errors.IntegrityError as e:
        if "1062" in str(e):
            return jsonify({'error': 'CPF already exists'}), 400
        else:
            return jsonify({'error': str(e)}), 500
    except KeyError as e:
        return jsonify({'error': f'Missing data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/balance', methods=['GET'])
def get_balance():
    if 'conta' not in session:
        return redirect(url_for('login'))
    
    conta = session['conta']
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
        if 'conta' not in session:
            conta_origem = request.form.get('conta_origem')
        else:
            conta_origem = session.get('conta')

        conta_destino = request.form.get('conta_destino')
        valor = request.form.get('valor')

        if not conta_origem or not conta_destino or not valor:
            return jsonify({'error': 'Missing form data'}), 400

        try:
            valor = float(valor)
        except ValueError:
            return jsonify({'error': 'Invalid value format'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Verificar se a conta de origem existe e obter saldo
            cursor.execute('SELECT saldo FROM contas WHERE conta = %s', (conta_origem,))
            saldo_origem = cursor.fetchone()

            if not saldo_origem:
                return jsonify({'error': 'Origin account not found'}), 404

            # Verificar se a conta de destino existe
            cursor.execute('SELECT saldo FROM contas WHERE conta = %s', (conta_destino,))
            saldo_destino = cursor.fetchone()

            if not saldo_destino:
                return jsonify({'error': 'Destination account not found'}), 404

            # Verificar saldo suficiente para a transferência
            if saldo_origem['saldo'] >= valor:
                cursor.execute('UPDATE contas SET saldo = saldo - %s WHERE conta = %s', (valor, conta_origem))
                cursor.execute('UPDATE contas SET saldo = saldo + %s WHERE conta = %s', (valor, conta_destino))
                conn.commit()

                # Obter o novo saldo da conta de origem
                cursor.execute('SELECT saldo FROM contas WHERE conta = %s', (conta_origem,))
                novo_saldo_origem = cursor.fetchone()

                return jsonify({
                    'message': 'Transfer successful',
                    'novo_saldo': novo_saldo_origem['saldo']
                }), 200
            else:
                return jsonify({'error': 'Insufficient funds'}), 400

        finally:
            cursor.close()
            conn.close()
    
    return render_template('transfer.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
