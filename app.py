from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error
from config import Config
import math

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

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

# Rutas principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# CRUD Productos
@app.route('/productos')
def productos():
    connection = get_db_connection()
    if not connection:
        return render_template('productos.html', productos=[])
    
    try:
        cursor = connection.cursor(dictionary=True)
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page
        
        # Obtener productos
        cursor.execute("SELECT * FROM productos ORDER BY fecha_creacion DESC LIMIT %s OFFSET %s", (per_page, offset))
        productos = cursor.fetchall()
        
        # Obtener total de productos
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

@app.route('/add_producto', methods=['GET', 'POST'])
def add_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        categoria = request.form['categoria']
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO productos (nombre, descripcion, precio, categoria) VALUES (%s, %s, %s, %s)",
                    (nombre, descripcion, precio, categoria)
                )
                connection.commit()
                flash('Producto agregado exitosamente!', 'success')
            except Error as e:
                flash(f'Error adding product: {e}', 'danger')
            finally:
                cursor.close()
                connection.close()
            return redirect(url_for('productos'))
    
    return render_template('add_producto.html')

@app.route('/edit_producto/<int:id>', methods=['GET', 'POST'])
def edit_producto(id):
    connection = get_db_connection()
    if not connection:
        return redirect(url_for('productos'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        categoria = request.form['categoria']
        
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, categoria=%s WHERE id=%s",
                (nombre, descripcion, precio, categoria, id)
            )
            connection.commit()
            flash('Producto actualizado exitosamente!', 'success')
        except Error as e:
            flash(f'Error updating product: {e}', 'danger')
        finally:
            cursor.close()
            connection.close()
        return redirect(url_for('productos'))
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
        producto = cursor.fetchone()
    except Error as e:
        flash(f'Error retrieving product: {e}', 'danger')
        producto = None
    finally:
        cursor.close()
        connection.close()
    
    return render_template('edit_producto.html', producto=producto)

@app.route('/delete_producto/<int:id>')
def delete_producto(id):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
            connection.commit()
            flash('Producto eliminado exitosamente!', 'success')
        except Error as e:
            flash(f'Error deleting product: {e}', 'danger')
        finally:
            cursor.close()
            connection.close()
    return redirect(url_for('productos'))

# CRUD Clientes
@app.route('/clientes')
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
        flash(f'Error retrieving clients: {e}', 'danger')
        clientes = []
        total_pages = 1
    finally:
        cursor.close()
        connection.close()
    
    return render_template('clientes.html', clientes=clientes, page=page, total_pages=total_pages)

@app.route('/add_cliente', methods=['GET', 'POST'])
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
                flash(f'Error adding client: {e}', 'danger')
            finally:
                cursor.close()
                connection.close()
            return redirect(url_for('clientes'))
    
    return render_template('add_cliente.html')

@app.route('/edit_cliente/<int:id>', methods=['GET', 'POST'])
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
            flash(f'Error updating client: {e}', 'danger')
        finally:
            cursor.close()
            connection.close()
        return redirect(url_for('clientes'))
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clientes WHERE id = %s", (id,))
        cliente = cursor.fetchone()
    except Error as e:
        flash(f'Error retrieving client: {e}', 'danger')
        cliente = None
    finally:
        cursor.close()
        connection.close()
    
    return render_template('edit_cliente.html', cliente=cliente)

@app.route('/delete_cliente/<int:id>')
def delete_cliente(id):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = %s", (id,))
            connection.commit()
            flash('Cliente eliminado exitosamente!', 'success')
        except Error as e:
            flash(f'Error deleting client: {e}', 'danger')
        finally:
            cursor.close()
            connection.close()
    return redirect(url_for('clientes'))

# Inventario
@app.route('/inventario')
def inventario():
    connection = get_db_connection()
    if not connection:
        return render_template('inventario.html', inventario=[])
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT i.*, p.nombre as producto_nombre 
            FROM inventario i 
            INNER JOIN productos p ON i.producto_id = p.id 
            ORDER BY i.fecha_actualizacion DESC
        """)
        inventario = cursor.fetchall()
    except Error as e:
        flash(f'Error retrieving inventory: {e}', 'danger')
        inventario = []
    finally:
        cursor.close()
        connection.close()
    
    return render_template('inventario.html', inventario=inventario)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)