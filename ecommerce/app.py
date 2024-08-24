from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from config import Config

app = Flask(__name__)
app.secret_key = 'supersecretkey'  
app.config.from_object(Config)

def get_db_connection():
    connection = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DATABASE']
    )
    return connection

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            session['user_id'] = user['id']
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
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
            connection.commit()
            flash('Registrado com sucesso. Faça o Login.', 'success')
            return redirect(url_for('login'))
        except Error as e:
            flash(f'Ocorreu um erro: {e}', 'danger')
        finally:
            cursor.close()
            connection.close()
    return render_template('register.html')

@app.route('/products', methods=['GET', 'POST'])
def products():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            action = request.form['action']
            product_id = request.form.get('product_id')
            name = request.form.get('name')
            price = request.form.get('price')

            if action == 'add':
                cursor.execute('INSERT INTO products (name, price) VALUES (%s, %s)', (name, price))
                connection.commit()
                flash('Produto adicionado com Sucesso', 'success')
            elif action == 'delete':
                cursor.execute('DELETE FROM products WHERE id = %s', (product_id,))
                connection.commit()
                flash('Produto deletado com Sucesso', 'success')
            elif action == 'edit':
                if name and price and product_id:
                    cursor.execute('UPDATE products SET name = %s, price = %s WHERE id = %s', (name, price, product_id))
                    connection.commit()
                    flash('Produto atualizado com Sucesso', 'success')
                else:
                    flash('Please provide all required fields.', 'warning')

        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
    except Error as e:
        flash(f'Ocorreu um erro: {e}', 'danger')
        products = []
    finally:
        cursor.close()
        connection.close()

    return render_template('products.html', products=products)

@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            if name and price:
                cursor.execute('UPDATE products SET name = %s, price = %s WHERE id = %s', (name, price, product_id))
                connection.commit()
                flash('Produto atualizado com sucesso', 'success')
                return redirect(url_for('products'))

        cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
        product = cursor.fetchone()
    except Error as e:
        flash(f'Ocorreu um erro: {e}', 'danger')
        product = None
    finally:
        cursor.close()
        connection.close()

    return render_template('edit_product.html', product=product)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
