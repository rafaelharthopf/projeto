from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('products'))
        else:
            flash('Nome e/ou senha inválido. Tente novamente.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registrado com sucesso. Faça o Login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Ocorreu um erro: {e}', 'danger')
    return render_template('register.html')

@app.route('/products', methods=['GET', 'POST'])
def products():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form['action']
        product_id = request.form.get('product_id')
        name = request.form.get('name')
        price = request.form.get('price')

        if action == 'add':
            new_product = Product(name=name, price=price)
            db.session.add(new_product)
            db.session.commit()
            flash('Produto adicionado com Sucesso', 'success')
        elif action == 'delete':
            product = Product.query.get(product_id)
            if product:
                db.session.delete(product)
                db.session.commit()
                flash('Produto deletado com Sucesso', 'success')
        elif action == 'edit':
            product = Product.query.get(product_id)
            if product and name and price:
                product.name = name
                product.price = price
                db.session.commit()
                flash('Produto atualizado com Sucesso', 'success')
            else:
                flash('Please provide all required fields.', 'warning')

    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get(product_id)
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        if product and name and price:
            product.name = name
            product.price = price
            db.session.commit()
            flash('Produto atualizado com sucesso', 'success')
            return redirect(url_for('products'))

    return render_template('edit_product.html', product=product)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    create_tables()  
    app.run(debug=False)
