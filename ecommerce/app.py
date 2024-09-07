from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask_sqlalchemy import SQLAlchemy
from config import Config
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from functools import wraps
from sqlalchemy.orm import relationship




app = Flask(__name__)
app.config.from_object('config.Config')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
            flash('Você não tem permissão para acessar essa página.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.current_user = None
    else:
        g.current_user = User.query.get(user_id)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    image_path = db.Column(db.String(255))
    
    user = relationship('User', backref='ads')
    category = relationship('Category', backref='ads')
    purchases = relationship('Purchase', backref='ad', cascade='all, delete-orphan')


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('questions', lazy=True))
    ad = db.relationship('Ad', backref=db.backref('questions', lazy=True))

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('answers', lazy=True))
    question = db.relationship('Question', backref=db.backref('answers', lazy=True))

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('favorites', lazy=True))
    ad = db.relationship('Ad', backref=db.backref('favorites', lazy=True))

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.id'), nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    ad = db.relationship('Ad', backref='cart_items')
    user = db.relationship('User', backref='cart_items')




def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    ads = Ad.query.all()
    return render_template('index.html', ads=ads)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nome e/ou senha inválido. Tente novamente.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = 'is_admin' in request.form

        try:
            new_user = User(username=username, password=password, is_admin=is_admin)
            db.session.add(new_user)
            db.session.commit()
            flash('Registrado com sucesso. Faça o Login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Ocorreu um erro: {e}', 'danger')

    is_admin_exists = User.query.filter_by(is_admin=True).first()
    return render_template('register.html', is_admin_exists=is_admin_exists)


@app.route('/admin/purchases')
@admin_required
def admin_purchases():
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        return redirect(url_for('login'))

    purchases = Purchase.query.join(User).add_columns(
        User.username, Purchase.date, Purchase.value, Purchase.ad_id
    ).all()

    return render_template('admin_purchases.html', purchases=purchases)





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
            flash('Produto adicionado com sucesso!', 'success')
        elif action == 'delete':
            product = Product.query.get(product_id)
            if product:
                db.session.delete(product)
                db.session.commit()
                flash('Produto deletado com sucesso!', 'success')
        elif action == 'edit':
            product = Product.query.get(product_id)
            if product and name and price:
                product.name = name
                product.price = price
                db.session.commit()
                flash('Produto atualizado com sucesso!', 'success')
            else:
                flash('Por favor, forneça todos os campos obrigatórios.', 'warning')

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
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('products'))

    return render_template('edit_product.html', product=product)

@app.route('/ads', methods=['GET', 'POST'])
@admin_required
def manage_ads():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        category_id = request.form['category_id']
        
        image_path = None
        if 'image' in request.files and allowed_file(request.files['image'].filename):
            image = request.files['image']
            filename = secure_filename(image.filename)
            image_path = filename  
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_ad = Ad(title=title, description=description, price=price, user_id=session['user_id'], category_id=category_id, image_path=image_path)
        db.session.add(new_ad)
        db.session.commit()
        flash('Anúncio criado com sucesso!', 'success')
        return redirect(url_for('index'))

    categories = Category.query.all()
    ads = Ad.query.all()
    return render_template('manage_ads.html', ads=ads, categories=categories)

@app.route('/ads/edit/<int:ad_id>', methods=['GET', 'POST'])
@admin_required
def edit_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    
    if request.method == 'POST':
        ad.title = request.form['title']
        ad.description = request.form['description']
        ad.price = request.form['price']
        ad.category_id = request.form['category_id']
        
        if 'image' in request.files and allowed_file(request.files['image'].filename):
            image = request.files['image']
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ad.image_path = filename
        
        db.session.commit()
        flash('Anúncio atualizado com sucesso!', 'success')
        return redirect(url_for('manage_ads'))

    categories = Category.query.all()
    return render_template('edit_ad.html', ad=ad, categories=categories)


@app.route('/ads/delete/<int:ad_id>', methods=['POST'])
@admin_required
def delete_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)

    if ad.image_path:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], ad.image_path))

    Purchase.query.filter_by(ad_id=ad_id).delete()

    db.session.delete(ad)
    db.session.commit()
    flash('Anúncio excluído com sucesso!', 'success')
    return redirect(url_for('manage_ads'))




@app.route('/categories', methods=['GET', 'POST'])
@admin_required
def manage_categories():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        flash('Categoria criada com sucesso!', 'success')

    categories = Category.query.all()
    return render_template('manage_categories.html', categories=categories)

@app.route('/favorites', methods=['GET', 'POST'])
def manage_favorites():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        ad_id = request.form.get('ad_id')
        action = request.form.get('action')

        if not ad_id or not action:
            flash('Dados inválidos.', 'danger')
            return redirect(url_for('manage_favorites'))

        if action == 'add':
            if not Favorite.query.filter_by(user_id=session['user_id'], ad_id=ad_id).first():
                new_favorite = Favorite(user_id=session['user_id'], ad_id=ad_id)
                db.session.add(new_favorite)
                db.session.commit()
                flash('Adicionado aos favoritos!', 'success')
            else:
                flash('O anúncio já está nos favoritos.', 'info')

        elif action == 'remove':
            favorite = Favorite.query.filter_by(user_id=session['user_id'], ad_id=ad_id).first()
            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                flash('Removido dos favoritos!', 'success')
            else:
                flash('Anúncio não encontrado nos favoritos.', 'warning')

        return redirect(url_for('manage_favorites'))

    user_id = session.get('user_id')
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    ads = Ad.query.filter(Ad.id.in_([fav.ad_id for fav in favorites])).all()
    
    return render_template('manage_favorites.html', favorites=ads)



@app.route('/purchase/<int:ad_id>', methods=['POST'])
def purchase(ad_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    ad = Ad.query.get(ad_id)
    if not ad:
        flash('Anúncio não encontrado.', 'danger')
        return redirect(url_for('manage_ads'))

    purchase = Purchase(user_id=session['user_id'], ad_id=ad_id, value=ad.price)
    db.session.add(purchase)
    db.session.commit()
    flash('Compra registrada com sucesso!', 'success')
    return redirect(url_for('manage_ads'))

@app.route('/add_to_cart/<int:ad_id>', methods=['POST'])
def add_to_cart(ad_id):
    quantity = int(request.form.get('quantity', 1)) 

    cart_item = CartItem.query.filter_by(ad_id=ad_id, user_id=session['user_id']).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        new_cart_item = CartItem(ad_id=ad_id, user_id=session['user_id'], quantity=quantity)
        db.session.add(new_cart_item)

    db.session.commit()
    flash('Item adicionado ao carrinho!', 'success')
    return redirect(url_for('cart'))



@app.route('/remove_from_cart/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart_item = CartItem.query.get(cart_item_id)
    if cart_item and cart_item.user_id == session['user_id']:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removido do carrinho!', 'success')
    else:
        flash('Item não encontrado ou você não tem permissão para removê-lo.', 'danger')

    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    return render_template('cart.html', cart_items=cart_items)


@app.route('/purchase_all', methods=['POST'])
def purchase_all():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    total_value = sum(item.ad.price * item.quantity for item in cart_items)

    for item in cart_items:
        purchase = Purchase(
            date=datetime.utcnow(), 
            user_id=session['user_id'], 
            ad_id=item.ad_id, 
            value=item.ad.price * item.quantity)
        db.session.add(purchase)
        db.session.delete(item)

    db.session.commit()
    flash('Compra realizada com sucesso! Seu produto está a caminho.', 'success')
    return redirect(url_for('purchase_history'))


@app.route('/ad/<int:ad_id>')
def ad_detail(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    return render_template('ad_detail.html', ad=ad)



@app.route('/purchase_history')
def purchase_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    purchases = Purchase.query.filter_by(user_id=session['user_id']).all()
    return render_template('purchase_history.html', purchases=purchases)



@app.route('/my_purchases')
def my_purchases():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    purchases = Purchase.query.filter_by(user_id=user_id).all()

    return render_template('my_purchases.html', purchases=purchases)



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
