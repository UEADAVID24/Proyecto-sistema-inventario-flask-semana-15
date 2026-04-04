# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================
from flask import Flask, render_template, request, redirect, url_for, send_file
from Conexion.conexion import obtener_conexion
from flask_login import LoginManager, UserMixin
from fpdf import FPDF
import io

# 🔐 SEGURIDAD
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================
# SERVICIOS
# ==========================================
from services.producto_service import (
    obtener_productos,
    insertar_producto,
    obtener_producto,
    actualizar_producto,
    eliminar_producto
)

from services.venta_service import obtener_ventas

# ==========================================
# CONFIGURACIÓN
# ==========================================
app = Flask(__name__)
app.secret_key = "clave_secreta"

login_manager = LoginManager()
login_manager.init_app(app)

# ==========================================
# USUARIO
# ==========================================
class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    return None

# ==========================================
# RUTAS PRINCIPALES
# ==========================================
@app.route('/')
def home():
    return render_template('panel.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/panel')
def panel():
    return render_template('panel.html')

@app.route('/clientes')
def clientes():
    return render_template('clientes.html')

# ==========================================
# FACTURA
# ==========================================
@app.route('/factura')
def factura():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT 
            f.id_factura,
            c.nombre,
            f.fecha,
            f.total
        FROM facturas f
        JOIN clientes c ON f.cliente_id = c.id_cliente
    """)

    datos = cursor.fetchall()
    conexion.close()

    return render_template('factura.html', datos=datos)

# ==========================================
# VENTAS
# ==========================================
@app.route('/ventas')
def ventas():
    datos = obtener_ventas()
    return render_template('ventas.html', ventas=datos)

# ==========================================
# LOGIN (🔥 CORREGIDO)
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT id_usuario, nombre, email, password FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        conexion.close()

        if user:
            if check_password_hash(user[3], password):
                return redirect(url_for('panel'))
            else:
                return "❌ Contraseña incorrecta"
        else:
            return "❌ Usuario no existe"

    return render_template('login.html')

# ==========================================
# REGISTRO
# ==========================================
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']

        password_segura = generate_password_hash(password)

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
            (nombre, email, password_segura)
        )

        conexion.commit()
        conexion.close()

        return redirect(url_for('panel'))

    return render_template('registro.html')

# ==========================================
# PRODUCTOS
# ==========================================
@app.route('/productos')
def productos():
    datos = obtener_productos()
    return render_template('productos/listar.html', productos=datos)

@app.route('/productos/agregar', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        insertar_producto(
            request.form['nombre'],
            int(request.form['cantidad']),
            float(request.form['precio'])
        )
        return redirect(url_for('productos'))

    return render_template('productos/agregar.html')

# ==========================================
# EDITAR PRODUCTO
# ==========================================
@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto = obtener_producto(id)

    if request.method == 'POST':
        actualizar_producto(
            id,
            request.form['nombre'],
            int(request.form['cantidad']),
            float(request.form['precio'])
        )
        return redirect(url_for('productos'))

    return render_template('productos/editar.html', producto=producto)

# ==========================================
# ELIMINAR PRODUCTO
# ==========================================
@app.route('/productos/eliminar/<int:id>')
def eliminar_producto_route(id):
    eliminar_producto(id)
    return redirect(url_for('productos'))

# ==========================================
# PDF
# ==========================================
@app.route('/reporte')
def reporte():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT 
            v.id,
            c.nombre,
            p.nombre,
            v.cantidad,
            v.precio,
            v.fecha
        FROM ventas v
        JOIN clientes c ON v.cliente_id = c.id_cliente
        JOIN productos p ON v.producto_id = p.id_producto
    """)

    datos = cursor.fetchall()
    conexion.close()

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "REPORTE DE VENTAS", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(200, 220, 255)

    pdf.cell(15, 10, "ID", border=1, align='C', fill=True)
    pdf.cell(35, 10, "Cliente", border=1, align='C', fill=True)
    pdf.cell(40, 10, "Producto", border=1, align='C', fill=True)
    pdf.cell(25, 10, "Cantidad", border=1, align='C', fill=True)
    pdf.cell(25, 10, "Precio", border=1, align='C', fill=True)
    pdf.cell(40, 10, "Fecha", border=1, align='C', fill=True)
    pdf.ln()

    pdf.set_font("Arial", "", 9)

    for v in datos:
        pdf.cell(15, 10, str(v[0]), border=1, align='C')
        pdf.cell(35, 10, str(v[1]), border=1)
        pdf.cell(40, 10, str(v[2]), border=1)
        pdf.cell(25, 10, str(v[3]), border=1, align='C')
        pdf.cell(25, 10, "$" + str(v[4]), border=1, align='C')
        pdf.cell(40, 10, str(v[5]), border=1)
        pdf.ln()

    total = sum([v[4] for v in datos])
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, f"TOTAL VENTAS: ${total}", ln=True, align='R')

    pdf_output = pdf.output(dest='S').encode('latin-1')

    return send_file(io.BytesIO(pdf_output),
                     download_name="reporte_ventas.pdf",
                     as_attachment=True)

# ==========================================
# RUN
# ==========================================
if __name__ == '__main__':
    app.run(debug=True)