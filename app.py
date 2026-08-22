from flask import Flask  # importa a classe principal em framework
from flask import (request, redirect, url_for, render_template,
                   make_response, session, flash)

app = Flask(__name__)
'''cria aplicação "__name__" e informa onde o arquivo esta localizado,
 aleḿ de encontrar outros arquivos de projeto, como os templates'''

app.secret_key = "troque-chave-em-producao"

produtos = [
    {"nome": "Mouse",
     "preco": 49.90,
     "estoque": 20,
     "categoria": "Acessórios",
     "descricao": "Mouse óptico com fio",
     },

    {"nome": "Teclado",
     "preco": 120.00,
     "estoque": 52,
     "categoria": "Acessórios",
     "descricao": "Teclado mecânico ABNT2",
     },

    {"nome": "Monitor",
     "preco": 800.00,
     "estoque": 50,
     "categoria": "Informática",
     "descricao": "Monitor de 24 polegadas",
     },

    {"nome": "Mouse Adaptado",
     "preco": 100.00,
     "estoque": 60,
     "categoria": "Acessórios",
     "descricao": "Mouse óptico sem fio",
     },
]


'''
Cookies: pequeno dado que o servidor pede para o navegador guardar, e que o navegador devolve
automaticamente em cada requisição seguinte para o mesmo site. É assim que uma aplicação web consegue
lembrar de alguma informação entre uma visita e outra, já que cada requisição HTTP é, por padrão, independente
das demais
'''

# Rotas
@app.route("/", methods=["GET", "POST"])
def index(): #é a view, ou seja, a função que vai acessar aquele endereço
    if request.method == "POST":
        nome_visitante = request.form.get("nome_visitante", "").strip()
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie("visitante", nome_visitante, max_age=60 * 60 * 24 * 30)
        return resp

    '''nome_visitante = request.cookies.get("visitante")
    return render_template("index.html", produtos=produtos, nome_visitante=nome_visitante)
    '''

    visitas_texto = request.cookies.get("visitas", 0)
    visitas = int(visitas_texto) + 1
    resp = make_response(render_template("index.html", produtos=produtos, nome_visitante=request.cookies.get("visitante"), visitas=visitas))

    resp.set_cookie("visitas", str(visitas), max_age= 60 * 60 * 24 * 30)

    return resp

@app.route("/esquecer")
def esquecer():
    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie("visitante")
    return resp

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        preco_texto = request.form.get("preco", "")
        estoque_texto = request.form.get("estoque", "")
        categoria = request.form.get("categoria", "")
        descricao = request.form.get("descricao", "").strip()

        confirmado = request.form.get("confirmado") == "sim"

        erros = []

        # Validar nome
        if not nome:
            erros.append("O nome é obrigatório.")

        # Nome duplicado
        if nome and any(produto["nome"].lower() == nome.lower() for produto in produtos):
            erros.append(f"Já existe um produto com o nome '{nome}'. Use um nome diferente.")

        # Validar categoria
        if not categoria:
            erros.append("Selecione uma categoria.")

        # Validar preço
        preco = None
        try:
            preco = float(preco_texto)
            if preco <= 0:
                erros.append("O preço precisa ser maior que zero.")
        except ValueError:
            erros.append("Preço inválido.")

        # Validar estoque
        estoque = None
        try:
            estoque = int(estoque_texto)
            if estoque < 0:
                erros.append("O estoque não pode ser negativo.")
        except ValueError:
            erros.append("Estoque inválido.")

        if erros:
            for erro in erros:
                flash(erro, "erro")
            return render_template("novo.html")

        if preco > 5000 and not confirmado:
            # Mostra o aviso e mantém os dados e clique em cadastrar novamente pata confirmar
            flash(
                f"O valor desse produto '{nome}' está correto? Confere novamente o valor {preco:.2f} se está correto para o cadastro.",
                "aviso")
            return render_template("novo.html",
                                   nome=nome,
                                   preco=preco_texto,
                                   estoque=estoque_texto,
                                   categoria=categoria,
                                   descricao=descricao,
                                   confirmado=True)

        produtos.append({
            "nome": nome,
            "preco": preco,
            "estoque": estoque,
            "categoria": categoria,
            "descricao": descricao,
        })


        session["cadastrados_na_sessao"] = session.get("cadastrados_na_sessao", 0) + 1

        flash("Produto cadastrado com sucesso!", "sucesso")
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


# COOKIE
@app.route("/cor", methods=["GET", "POST"])
def cor():
    if request.method == "POST":
        cor_escolhida = request.form.get("cor", "")  # Corrigido: name="cor"
        resp = make_response(redirect(url_for("cor")))
        resp.set_cookie("cor_favorita", cor_escolhida)
        return resp

    cor_salva = request.cookies.get("cor_favorita", "nenhuma cor salva ainda")

    return f"""
    <p>Cor salva atualmente: {cor_salva}</p>
    <form method="POST">
        <input type="text" name="cor">
        <button type="submit">Salvar</button>
    </form>"""


@app.route("/perfil")
def perfil():
    nome_visitante = request.cookies.get("visitante")

    if not nome_visitante:
        flash("Você ainda não se identificou.Use o fomrulário na página inicial para slavar o seu nome", "aviso")

    produtos_cadastrados = session.get("cadastrados_na_sessao", "0")

    visitas_texto = request.cookies.get("visitas", "0")
    visitas = int (visitas_texto)

    return render_template("perfil.html", nome_visitante=nome_visitante, produtos_cadastrados=produtos_cadastrados,visitas=visitas)


#TEMA Esuro e Claro

@app.route("/tema/<escolha>")
def tema(escolha):

    pagina_anterior = request.referrer or url_for("index")

    resp = make_response(redirect(pagina_anterior))

    if escolha in ["claro", "escuro"]:
        resp.set_cookie("tema", escolha, max_age=60 * 60 * 24 * 30)
        flash(f"Tema alterado para {escolha}!", "sucesso")
    else:
        flash("Opção de tema inválida!", "erro")

    return resp

if __name__ == "__main__":
    app.run(debug=True)

