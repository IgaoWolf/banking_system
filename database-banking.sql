USE banking;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cpf VARCHAR(14) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    sobrenome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    telefone VARCHAR(15) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    conta VARCHAR(20) UNIQUE NOT NULL
);


INSERT INTO usuarios (cpf, nome, sobrenome, email, telefone, senha, conta)
VALUES ('12345678901', 'Igor', 'Wolf', 'igaowolf@gmail.com', '999999999', 'senha123', '12345');

CREATE TABLE contas (
    conta VARCHAR(20) PRIMARY KEY,
    saldo DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    usuario_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

INSERT INTO contas (conta, saldo, usuario_id)
VALUES ('12345', 1000.00, 1);

## Ajuste para teste de criação de usuários utilizando o mesmo cpf

SELECT cpf, COUNT(*)
FROM usuarios
GROUP BY cpf
HAVING COUNT(*) > 1;

ALTER TABLE usuarios ADD UNIQUE (cpf);