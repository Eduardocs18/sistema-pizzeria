from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)

from database import get_connection
from datetime import datetime

app = Flask(__name__)

app.secret_key = 'luciferpizza123'

USUARIO = 'admin'
PASSWORD = 'LuiferPizza2026#'

# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        usuario = request.form['usuario']
        password = request.form['password']

        if usuario == USUARIO and password == PASSWORD:

            session['usuario'] = usuario

            return redirect('/')

    return render_template('login.html')

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

# =========================
# DASHBOARD
# =========================

@app.route('/')
def index():

    if 'usuario' not in session:
        return redirect('/login')

    connection = get_connection()

    productos = connection.execute(
        'SELECT * FROM productos'
    ).fetchall()

    ingresos = connection.execute(
        'SELECT * FROM ingresos'
    ).fetchall()

    gastos = connection.execute(
        'SELECT * FROM gastos'
    ).fetchall()

    pedidos = connection.execute(
    '''
    SELECT pedidos.*, pizzas.nombre AS pizza_nombre
    FROM pedidos
    JOIN pizzas ON pedidos.pizza_id = pizzas.id
    ORDER BY pedidos.id DESC
    '''
    ).fetchall()

    pizzas = connection.execute(
        'SELECT * FROM pizzas'
    ).fetchall()

    total_ingresos = connection.execute(
        'SELECT SUM(monto) FROM ingresos'
    ).fetchone()[0]

    total_gastos = connection.execute(
        'SELECT SUM(monto) FROM gastos'
    ).fetchone()[0]

    connection.close()

    total_ingresos = total_ingresos or 0
    total_gastos = total_gastos or 0

    balance = total_ingresos - total_gastos

    return render_template(
        'index.html',
        productos=productos,
        ingresos=ingresos,
        gastos=gastos,
        total_ingresos=total_ingresos,
        total_gastos=total_gastos,
        balance=balance,
        pedidos=pedidos,
        pizzas=pizzas,
    )

# =========================
# PRODUCTOS
# =========================

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():

    if 'usuario' not in session:
        return redirect('/login')

    nombre = request.form['nombre']
    categoria = request.form['categoria']
    stock = request.form['stock']
    precio = request.form['precio']

    connection = get_connection()

    connection.execute('''
        INSERT INTO productos (nombre, categoria, stock, precio)
        VALUES (?, ?, ?, ?)
    ''', (nombre, categoria, stock, precio))

    connection.commit()
    connection.close()

    return redirect('/')

@app.route('/editar_producto/<int:id>', methods=['POST'])
def editar_producto(id):

    if 'usuario' not in session:
        return redirect('/login')

    nombre = request.form['nombre']
    categoria = request.form['categoria']
    stock = request.form['stock']
    precio = request.form['precio']

    connection = get_connection()

    connection.execute('''
        UPDATE productos
        SET nombre = ?, categoria = ?, stock = ?, precio = ?
        WHERE id = ?
    ''', (nombre, categoria, stock, precio, id))

    connection.commit()
    connection.close()

    return redirect('/')

@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):

    if 'usuario' not in session:
        return redirect('/login')

    connection = get_connection()

    connection.execute(
        'DELETE FROM productos WHERE id = ?',
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect('/')

# =========================
# INGRESOS
# =========================

@app.route('/agregar_ingreso', methods=['POST'])
def agregar_ingreso():

    if 'usuario' not in session:
        return redirect('/login')

    descripcion = request.form['descripcion']
    monto = request.form['monto']
    fecha = datetime.now().strftime('%Y-%m-%d')

    connection = get_connection()

    connection.execute('''
        INSERT INTO ingresos (descripcion, monto, fecha)
        VALUES (?, ?, ?)
    ''', (descripcion, monto, fecha))

    connection.commit()
    connection.close()

    return redirect('/')

@app.route('/eliminar_ingreso/<int:id>')
def eliminar_ingreso(id):

    if 'usuario' not in session:
        return redirect('/login')

    connection = get_connection()

    connection.execute(
        'DELETE FROM ingresos WHERE id = ?',
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect('/')

# =========================
# GASTOS
# =========================

@app.route('/agregar_gasto', methods=['POST'])
def agregar_gasto():

    if 'usuario' not in session:
        return redirect('/login')

    descripcion = request.form['descripcion']
    monto = request.form['monto']
    fecha = datetime.now().strftime('%Y-%m-%d')

    connection = get_connection()

    connection.execute('''
        INSERT INTO gastos (descripcion, monto, fecha)
        VALUES (?, ?, ?)
    ''', (descripcion, monto, fecha))

    connection.commit()
    connection.close()

    return redirect('/')

@app.route('/eliminar_gasto/<int:id>')
def eliminar_gasto(id):

    if 'usuario' not in session:
        return redirect('/login')

    connection = get_connection()

    connection.execute(
        'DELETE FROM gastos WHERE id = ?',
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect('/')

# =========================
# PEDIDOS
# =========================

@app.route('/agregar_pedido', methods=['POST'])
def agregar_pedido():

    if 'usuario' not in session:
        return redirect('/login')

    cliente = request.form['cliente']
    pizza_id = int(request.form['pizza_id'])
    tamano = request.form['tamano']
    cantidad = int(request.form['cantidad'])

    connection = get_connection()

    pizza = connection.execute(
        'SELECT * FROM pizzas WHERE id = ?',
        (pizza_id,)
    ).fetchone()

    # =========================
    # PRECIOS
    # =========================

    if tamano == 'Personal':
        precio_unitario = pizza['precio_personal']

    elif tamano == 'Small':
        precio_unitario = pizza['precio_small']

    elif tamano == 'Mediana':
        precio_unitario = pizza['precio_mediana']

    else:
        precio_unitario = pizza['precio_familiar']

    total = precio_unitario * cantidad

    fecha = datetime.now().strftime('%Y-%m-%d')

    # =========================
    # GUARDAR PEDIDO
    # =========================

    connection.execute('''
        INSERT INTO pedidos
        (cliente, pizza_id, tamano, cantidad, total, fecha)

        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        cliente,
        pizza_id,
        tamano,
        cantidad,
        total,
        fecha
    ))

    # =========================
    # REGISTRAR INGRESO
    # =========================

    descripcion = f'Pedido - {pizza["nombre"]}'

    connection.execute('''
        INSERT INTO ingresos
        (descripcion, monto, fecha)

        VALUES (?, ?, ?)
    ''', (
        descripcion,
        total,
        fecha
    ))

    # =========================
    # MULTIPLICADORES
    # =========================

    multiplicadores = {
        'Personal': 0.7,
        'Small': 1,
        'Mediana': 1.5,
        'Familiar': 2.2
    }

    multiplicador = multiplicadores[tamano]

    # =========================
    # RECETAS
    # =========================

    recetas = connection.execute(
        'SELECT * FROM recetas WHERE pizza_id = ?',
        (pizza_id,)
    ).fetchall()

    # =========================
    # DESCONTAR INVENTARIO
    # =========================

    for receta in recetas:

        cantidad_usada = (
            receta['cantidad']
            * multiplicador
            * cantidad
        )

        connection.execute('''
            UPDATE productos
            SET stock = stock - ?
            WHERE id = ?
        ''', (
            cantidad_usada,
            receta['ingrediente_id']
        ))

    connection.commit()
    connection.close()

    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)