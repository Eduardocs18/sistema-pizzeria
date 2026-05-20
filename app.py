from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)

from database import get_connection
from datetime import datetime, timedelta

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
        'SELECT * FROM ingresos ORDER BY id DESC'
    ).fetchall()

    gastos = connection.execute(
        'SELECT * FROM gastos ORDER BY id DESC'
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

    # =========================
    # DASHBOARD DIARIO
    # =========================

    hoy = datetime.now().strftime('%Y-%m-%d')

    total_ingresos = connection.execute(
    '''
    SELECT SUM(monto)
    FROM ingresos
    WHERE fecha = ?
    ''',
    (hoy,)
    ).fetchone()[0]

    total_gastos = connection.execute(
    '''
    SELECT SUM(monto)
    FROM gastos
    WHERE fecha = ?
    ''',
    (hoy,)
    ).fetchone()[0]

    total_ingresos = total_ingresos or 0
    total_gastos = total_gastos or 0

    balance = total_ingresos - total_gastos

    # =========================
    # FILTRO REPORTES
    # =========================

    filtro = request.args.get('filtro', 'diario')

    fecha_inicio = hoy

    if filtro == 'semanal':

        fecha_inicio = (
            datetime.now() - timedelta(days=7)
        ).strftime('%Y-%m-%d')

    elif filtro == 'quincenal':

        fecha_inicio = (
            datetime.now() - timedelta(days=15)
        ).strftime('%Y-%m-%d')

    elif filtro == 'mensual':

        fecha_inicio = (
            datetime.now() - timedelta(days=30)
        ).strftime('%Y-%m-%d')

    # =========================
    # INGRESOS FILTRADOS
    # =========================

    ingresos_filtrados = connection.execute(
    '''
    SELECT *
    FROM ingresos
    WHERE fecha >= ?
    ORDER BY fecha DESC
    ''',
    (fecha_inicio,)
    ).fetchall()

    total_ingresos_filtrados = connection.execute(
    '''
    SELECT SUM(monto)
    FROM ingresos
    WHERE fecha >= ?
    ''',
    (fecha_inicio,)
    ).fetchone()[0]

    # =========================
    # GASTOS FILTRADOS
    # =========================

    gastos_filtrados = connection.execute(
    '''
    SELECT *
    FROM gastos
    WHERE fecha >= ?
    ORDER BY fecha DESC
    ''',
    (fecha_inicio,)
    ).fetchall()

    total_gastos_filtrados = connection.execute(
    '''
    SELECT SUM(monto)
    FROM gastos
    WHERE fecha >= ?
    ''',
    (fecha_inicio,)
    ).fetchone()[0]

    # =========================
    # PIZZAS MÁS VENDIDAS
    # =========================

    pizzas_top = connection.execute(
    '''
    SELECT pizzas.nombre,
           SUM(pedidos.cantidad) AS total_vendidas

    FROM pedidos

    JOIN pizzas
    ON pedidos.pizza_id = pizzas.id

    WHERE pedidos.estado = 'Confirmado'
    AND pedidos.fecha >= ?

    GROUP BY pizzas.nombre

    ORDER BY total_vendidas DESC

    LIMIT 5
    ''',
    (fecha_inicio,)
    ).fetchall()

    total_ingresos_filtrados = (
        total_ingresos_filtrados or 0
    )

    total_gastos_filtrados = (
        total_gastos_filtrados or 0
    )

    balance_filtrado = (
        total_ingresos_filtrados
        - total_gastos_filtrados
    )

    connection.close()

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

    filtro=filtro,

    ingresos_filtrados=ingresos_filtrados,
    gastos_filtrados=gastos_filtrados,

    total_ingresos_filtrados=total_ingresos_filtrados,
    total_gastos_filtrados=total_gastos_filtrados,
    balance_filtrado=balance_filtrado,

    pizzas_top=pizzas_top
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
        INSERT INTO productos
        (nombre, categoria, stock, precio)

        VALUES (?, ?, ?, ?)
    ''', (
        nombre,
        categoria,
        stock,
        precio
    ))

    connection.commit()
    connection.close()

    return redirect('/#inventario')

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
        SET nombre = ?,
            categoria = ?,
            stock = ?,
            precio = ?
        WHERE id = ?
    ''', (
        nombre,
        categoria,
        stock,
        precio,
        id
    ))

    connection.commit()
    connection.close()

    return redirect('/#inventario')

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

    return redirect('/#inventario')

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
        INSERT INTO ingresos
        (descripcion, monto, fecha)

        VALUES (?, ?, ?)
    ''', (
        descripcion,
        monto,
        fecha
    ))

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

    return redirect('/#ingresos')

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
        INSERT INTO gastos
        (descripcion, monto, fecha)

        VALUES (?, ?, ?)
    ''', (
        descripcion,
        monto,
        fecha
    ))

    connection.commit()
    connection.close()

    return redirect('/#gastos')

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

    return redirect('/#gastos')

# =========================
# PEDIDOS
# =========================

@app.route('/agregar_pedido', methods=['POST'])
def agregar_pedido():

    if 'usuario' not in session:
        return redirect('/login')

    cliente = request.form['cliente']

    pizza_id = int(
        request.form['pizza_id']
    )

    tamano = request.form['tamano']

    cantidad = int(
        request.form['cantidad']
    )

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
        (
            cliente,
            pizza_id,
            tamano,
            cantidad,
            total,
            fecha,
            estado
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        cliente,
        pizza_id,
        tamano,
        cantidad,
        total,
        fecha,
        'Pendiente'
    ))

    connection.commit()
    connection.close()

    return redirect('/#pedidos')

# =========================
# CONFIRMAR PEDIDO
# =========================

@app.route('/confirmar_pedido/<int:id>')
def confirmar_pedido(id):

    if 'usuario' not in session:
        return redirect('/login')

    connection = get_connection()

    pedido = connection.execute(
        'SELECT * FROM pedidos WHERE id = ?',
        (id,)
    ).fetchone()

    if pedido['estado'] != 'Pendiente':

        connection.close()

        return redirect('/#pedidos')

    pizza = connection.execute(
        'SELECT * FROM pizzas WHERE id = ?',
        (pedido['pizza_id'],)
    ).fetchone()

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
        pedido['total'],
        pedido['fecha']
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

    multiplicador = multiplicadores[
        pedido['tamano']
    ]

    # =========================
    # RECETAS
    # =========================

    recetas = connection.execute(
        'SELECT * FROM recetas WHERE pizza_id = ?',
        (pedido['pizza_id'],)
    ).fetchall()

    # =========================
    # DESCONTAR INVENTARIO
    # =========================

    for receta in recetas:

        cantidad_usada = (
            receta['cantidad']
            * multiplicador
            * pedido['cantidad']
        )

        connection.execute('''
            UPDATE productos
            SET stock = stock - ?
            WHERE id = ?
        ''', (
            cantidad_usada,
            receta['ingrediente_id']
        ))

    # =========================
    # CAMBIAR ESTADO
    # =========================

    connection.execute('''
        UPDATE pedidos
        SET estado = 'Confirmado'
        WHERE id = ?
    ''', (id,))

    connection.commit()
    connection.close()

    return redirect('/#pedidos')

# =========================
# CANCELAR PEDIDO
# =========================

@app.route('/cancelar_pedido/<int:id>')
def cancelar_pedido(id):

    if 'usuario' not in session:
        return redirect('/login')

    connection = get_connection()

    connection.execute('''
        UPDATE pedidos
        SET estado = 'Cancelado'
        WHERE id = ?
    ''', (id,))

    connection.commit()
    connection.close()

    return redirect('/#pedidos')



if __name__ == '__main__':
    app.run(
    host='0.0.0.0',
    port=5002,
    debug=False
)