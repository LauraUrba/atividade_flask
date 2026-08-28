#teste se esta funcionando o bando de dados por conta de erros que estava acontecendo durante o processo
import pymysql

try:
    connection = pymysql.connect(
        host='127.0.0.1',
        user='laura',
        password='Laura0601!',
        database='catalogo_produtos'
    )
    print("Conexão bem sucedida!")
    print("Usuário laura conectado com sucesso!")
    connection.close()
except Exception as e:
    print(f"Erro: {e}")
