from flask import Flask, render_template  # importa a classe principal em framework
from flask import request, redirect, url_for

app = Flask(__name__)
'''cria aplicação "__name__" e informa onde o arquivo esta localizado,
 aleḿ de encontrar outros arquivos de projeto, como os templates'''

produtos = [
    {"nome": "Mouse", "preco": 49.90, "estoque": 20},
    {"nome": "Teclado", "preco": 120.00, "estoque": 52},
    {"nome": "Monitor", "preco": 800.00, "estoque": 50},
    {"nome": "Mouse Adaptado", "preco": 100.00, "estoque": 60},
]

@app.route("/")
def index(): #é a view, ou seja, a função que vai acessar aquele endereço
    return render_template("index.html", produtos=produtos)

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        nome = request.form["nome"]
        preco = float(request.form["preco"])
        estoque = int(request.form["estoque"])
        produtos.append({"nome": nome, "preco": preco, "estoque": estoque})

        if preco <= 0:
            erro = "Erro: O preço deve ser maior que zero!"
            return render_template("novo.html", erro=erro, nome=nome, preco=preco, estoque=estoque)

        return redirect(url_for("index"))
    return render_template("novo.html")


@app.route("/produtos/caros")
def caros():
    produtos_caros = [produto for produto in produtos if produto["preco"] > 100]
    return render_template("prodCaros.html", produtos=produtos_caros)

@app.route("/remover/<nome_produto>", methods=["DELET", "POST"])
def remover(nome_produto):
    for produto in produtos:
        if produto["nome"] == nome_produto:
            produtos.remove(produto)

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

