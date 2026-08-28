from flask import Flask  # importa a classe principal em framework
from flask import (request, redirect, url_for, render_template,
                   make_response, session, flash)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import default

app = Flask(__name__)
'''cria aplicação "__name__" e informa onde o arquivo esta localizado,
 aleḿ de encontrar outros arquivos de projeto, como os templates'''

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://laura:Laura0601!@127.0.0.1/catalogo_produtos"
)

db = SQLAlchemy(app)

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, default=0)
    categoria = db.Column(db.String(50))
    descricao = db.Column(db.Text)


def popular_banco():
    if Produto.query.count() == 0:
        db.session.add(Produto(
            nome="Mouse", preco=49.90,
            estoque=20, 
            categoria="Acessórios",
            descricao="Mouse óptico com fio.",
        ))
        db.session.add(Produto(
            nome="Teclado", preco=120.00,
            estoque=52, 
            categoria="Acessórios",
            descricao="Teclado mecânico ABNT2.",
        ))
        db.session.add(Produto(
            nome="Monitor", preco=800.00,
            estoque=50, 
            categoria="Informática",
            descricao="Monitor de 24 polegadas.",
        ))
        db.session.commit()

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
def index():
    # Verificar se tem ordenação
    ordem = request.args.get("ordem", "")

    # Buscar produtos com ordenação
    if ordem == "menor":
        produtos = Produto.query.order_by(Produto.preco.asc()).all()
    elif ordem == "maior":
        produtos = Produto.query.order_by(Produto.preco.desc()).all()
    else:
        produtos = Produto.query.all()  # Ordem padrão

    if request.method == "POST":
        nome_visitante = request.form.get("nome_visitante", "").strip()
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie("visitante", nome_visitante, max_age=60 * 60 * 24 * 30)
        return resp

    visitas_texto = request.cookies.get("visitas", "0")
    visitas = int(visitas_texto) + 1
    resp = make_response(render_template("index.html",
                                         produtos=produtos,
                                         nome_visitante=request.cookies.get("visitante"),
                                         visitas=visitas,
                                         ordem=ordem)) 

    resp.set_cookie("visitas", str(visitas), max_age=60 * 60 * 24 * 30)
    return resp

@app.route("/esquecer")
def esquecer():
    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie("visitante")
    return resp

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/produto/<int:produto_id>")
def detalhe_produto(produto_id):
    produto = db.get_or_404(Produto, produto_id)
    return render_template("detalhe.html", produto=produto)

@app.route("/produto/<int:produto_id>/editar", methods=["GET", "POST"])
def editar_produto(produto_id):
    produto = db.get_or_404(Produto, produto_id)
    if request.method == "POST":
        produto.nome = request.form.get("nome", "").strip()
        produto.preco = float(request.form.get("preco", 0))
        produto.estoque = int(request.form.get("estoque", ""))
        produto.categoria = request.form.get("categoria", "")
        produto.descricao = request.form.get("descricao", "").strip()
        db.session.commit()
        flash("Produto atualizado com sucesso!", "sucesso")
        return redirect(url_for("index"))

    return render_template("editar.html", produto=produto)

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
        if nome and Produto.query.filter(Produto.nome.ilike(nome)).first():
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

        novo_produto = Produto(
            nome=nome,
            preco=preco,
            estoque=estoque,
            categoria=categoria,
            descricao=descricao
        )

        session["cadastrados_na_sessao"] = session.get("cadastrados_na_sessao", 0) + 1

        db.session.add(novo_produto)
        db.session.commit()

        flash("Produto cadastrado com sucesso!", "sucesso")
        return redirect(url_for("index"))

    return render_template("novo.html")


@app.route("/produtos/caros")
def caros():
    produtos_caros = Produto.query.filter(Produto.preco > 100).all()
    return render_template("prodCaros.html", produtos=produtos_caros)


@app.route("/produto/<int:produto_id>/remover", methods=["GET"])
def confirmar_remocao(produto_id):
    produto = db.get_or_404(Produto, produto_id)
    return render_template("confirmar_remocao.html", produto=produto)

@app.route("/produto/<int:produto_id>/deletar", methods=["POST"])
def deletar_produto(produto_id):
    produto = db.get_or_404(Produto, produto_id)
    db.session.delete(produto)
    db.session.commit()
    flash("Produto removido com sucesso!", "sucesso")
    return redirect(url_for("index"))

# COOKIE
@app.route("/cor", methods=["GET", "POST"])
def cor():
    if request.method == "POST":
        cor_escolhida = request.form.get("cor", "")
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
        flash("Você ainda não se identificou. Use o formulário na página inicial para salvar o seu nome", "aviso")

    produtos_cadastrados = session.get("cadastrados_na_sessao", "0")

    visitas_texto = request.cookies.get("visitas", "0")
    visitas = int(visitas_texto)

    return render_template("perfil.html",
                          nome_visitante=nome_visitante,
                          produtos_cadastrados=produtos_cadastrados,
                          visitas=visitas)

@app.route("/categoria<nome_categoria>")
def categoria():
    produtos_filtrados = Produto.query.filter_by(categoria=nome_categoria).all()

    return render_template("index.html",
                           produtos=produtos_filtrados,
                           nome_visitante=request.cookies.get("visitante"),
                           visitas=request.cookies.get("visitas", 0))


# TEMA Escuro e Claro
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


with app.app_context():
     db.create_all()
     nova = Tarefa(titulo="Estudar Flask")
     db.session.add(nova)
     db.session.commit()



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        popular_banco()
    app.run(debug=True)
