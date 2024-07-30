## 1. Atualizar o Sistema

Primeiro, atualize seu sistema para garantir que você tenha as últimas atualizações e pacotes:

```bash

sudo apt update
sudo apt upgrade
```

## 2. Instalar o MariaDB

Instale o MariaDB para gerenciar seu banco de dados:

```bash

sudo apt install mariadb-server mariadb-client
```

## 3. Configurar o MariaDB

Configure o MariaDB para maior segurança e crie o banco de dados e usuário necessários:

```bash

sudo mysql_secure_installation

sudo mysql -u root -p
```

```sql
CREATE DATABASE banking;
CREATE USER 'bank'@'localhost' IDENTIFIED BY 'passwdbank';
GRANT ALL PRIVILEGES ON banking.* TO 'bank'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 4. Instalar o Python e Dependências

Instale o Python e pacotes necessários:

```bash

sudo apt install python3 python3-pip python3-venv
```

Crie um ambiente virtual para seu projeto:

``` bash

python3 -m venv venv
source venv/bin/activate
```

```bash
pip install flask flask-mysql mysql-connector-python
```

## 5. Instalar o Nginx e efetuar as configurações

```bash
sudo apt install nginx
```

Crie o arquivo 

```bash
sudo vim /etc/nginx/sites-available/banking
```

Edite-o 

```bash
server {
    listen 80;
    server_name 192.168.3.71;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Ajuste agora seu nginx 

```bash
sudo ln -s /etc/nginx/sites-available/banking /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```


## Querys API 

```bash

source venv/bin/activate
python app.py

```

Login:

```bash
curl -X POST http://192.168.3.71:5000/login -H "Content-Type: application/json" -d '{"conta": "12345", "senha": "senha123"}'
```

Criar Conta:

```bash
curl -X POST http://192.168.3.71:5000/create_account -H "Content-Type: application/json" -d '{"cpf": "98765432100", "nome": "Maria", "sobrenome": "Silva", "email": "maria.silva@example.com", "telefone": "888888888", "senha": "maria123"}'
```

Retorno:
```bash
{
  "conta": "7724518141",
  "message": "Account created successfully"
}
```

Login

```bash
curl -X POST http://192.168.3.71:5000/login -H "Content-Type: application/json" -d '{"conta": "7724518141", "senha": "maria123"}'
```

Verificar Saldo:

```bash

curl "http://192.168.3.71:5000/balance?conta=7724518141"
```

Saque:

```bash

curl -X POST http://192.168.3.71:5000/withdraw -H "Content-Type: application/json" -d '{"conta": "12345", "valor": 100.00}'
```

Transferência:

```bash
curl -X POST http://192.168.3.71:5000/transfer -H "Content-Type: application/json" -d '{"conta_origem": "12345", "conta_destino": "7724518141", "valor": 50.00}'
```

Retornos de Transferência:

```bash
curl -X POST http://192.168.3.71:5000/transfer -H "Content-Type: application/json" -d '{"conta_origem": "12345", "conta_destino": "7724518141", "valor": 50.00}'
{
  "message": "Transfer successful"
}
```

```bash
curl "http://192.168.3.71:5000/balance?conta=12345"
{
  "saldo": "850.00"
}
curl "http://192.168.3.71:5000/balance?conta=7724518141"
{
  "saldo": "50.00"
}
```