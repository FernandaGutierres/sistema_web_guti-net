from flask import Flask, render_template, request, redirect, session, url_for, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from config import Config
import math

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# --- Función para requerir login ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Conexión a base de datos ---
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            port=Config.MYSQL_PORT
        )
        return connection
    except Error as e:
        flash(f'Error connecting to MySQL: {e}', 'danger')
        return None

# --- Rutas principales ---
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# --- Registro de usuario ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO usuarios (username, password, email) VALUES (%s, %s, %s)",
                    (username, hashed_password, email)
                )
                connection.commit()
                flash('Usuario registrado correctamente', 'success')
                return redirect(url_for('login'))
            except Error as e:
                flash(f'Error al registrar usuario: {e}', 'danger')
            finally:
                cursor.close()
                connection.close()
    return render_template('register.html')

# --- Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM usuarios WHERE username=%s", (username,))
                user = cursor.fetchone()
                if user and check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    flash('Login exitoso!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Usuario o contraseña incorrectos', 'danger')
            finally:
                cursor.close()
                connection.close()
    return render_template('login.html')

# --- Logout ---
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))

# --- Ejemplo de ruta protegida ---
@app.route('/productos')
@login_required
def productos():
    connection = get_db_connection()
    if not connection:
        return render_template('productos.html', productos=[])

    try:
        cursor = connection.cursor(dictionary=True)
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page

        cursor.execute("SELECT * FROM productos ORDER BY fecha_creacion DESC LIMIT %s OFFSET %s", (per_page, offset))
        productos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as total FROM productos")
        total = cursor.fetchone()['total']
        total_pages = math.ceil(total / per_page)

    except Error as e:
        flash(f'Error retrieving products: {e}', 'danger')
        productos = []
        total_pages = 1
    finally:
        cursor.close()
        connection.close()

    return render_template('productos.html', productos=productos, page=page, total_pages=total_pages)

# -----------------------------
# CRUD Clientes
# -----------------------------
@app.route('/clientes')
@login_required
def clientes():
    connection = get_db_connection()
    if not connection:
        return render_template('clientes.html', clientes=[])

    try:
        cursor = connection.cursor(dictionary=True)
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page

        cursor.execute("SELECT * FROM clientes ORDER BY fecha_registro DESC LIMIT %s OFFSET %s", (per_page, offset))
        clientes = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as total FROM clientes")
        total = cursor.fetchone()['total']
        total_pages = math.ceil(total / per_page)
    except Error as e:
        flash(f'Error al obtener clientes: {e}', 'danger')
        clientes, total_pages = [], 1
    finally:
        cursor.close()
        connection.close()

    return render_template('clientes.html', clientes=clientes, page=page, total_pages=total_pages)

@app.route('/add_cliente', methods=['GET', 'POST'])
@login_required
def add_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']

        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO clientes (nombre, email, telefono, direccion) VALUES (%s, %s, %s, %s)",
                    (nombre, email, telefono, direccion)
                )
                connection.commit()
                flash('Cliente agregado exitosamente!', 'success')
            except Error as e:
                flash(f'Error al agregar cliente: {e}', 'danger')
            finally:
                cursor.close()
                connection.close()
            return redirect(url_for('clientes'))

    return render_template('add_cliente.html')

@app.route('/edit_cliente/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_cliente(id):
    connection = get_db_connection()
    if not connection:
        return redirect(url_for('clientes'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']

        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE clientes SET nombre=%s, email=%s, telefono=%s, direccion=%s WHERE id=%s",
                (nombre, email, telefono, direccion, id)
            )
            connection.commit()
            flash('Cliente actualizado exitosamente!', 'success')
        except Error as e:
            flash(f'Error al actualizar cliente: {e}', 'danger')
        finally:
            cursor.close()
            connection.close()
        return redirect(url_for('clientes'))

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clientes WHERE id=%s", (id,))
        cliente = cursor.fetchone()
    except Error as e:
        flash(f'Error al obtener cliente: {e}', 'danger')
        cliente = None
    finally:
        cursor.close()
        connection.close()

    return render_template('edit_cliente.html', cliente=cliente)

@app.route('/delete_cliente/<int:id>')
@login_required
def delete_cliente(id):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM clientes WHERE id=%s", (id,))
            connection.commit()
            flash('Cliente eliminado exitosamente!', 'success')
        except Error as e:
            flash(f'Error al eliminar cliente: {e}', 'danger')
        finally:
            cursor.close()
            connection.close()
    return redirect(url_for('clientes'))

# -----------------------------
# Inventario
# -----------------------------
@app.route('/inventario')
@login_required
def inventario():
    connection = get_db_connection()
    if not connection:
        return render_template('inventario.html', inventario=[])

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT i.*, p.nombre AS producto_nombre 
            FROM inventario i 
            INNER JOIN productos p ON i.producto_id = p.id 
            ORDER BY i.fecha_actualizacion DESC
        """)
        inventario = cursor.fetchall()
    except Error as e:
        flash(f'Error al obtener inventario: {e}', 'danger')
        inventario = []
    finally:
        cursor.close()
        connection.close()

    return render_template('inventario.html', inventario=inventario)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
