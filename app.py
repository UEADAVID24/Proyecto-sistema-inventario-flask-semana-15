from flask import Flask, render_template, request, redirect, url_for, send_file
from Conexion.conexion import obtener_conexion
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from fpdf import FPDF
import io

# 🔥 IMPORTAR SERVICES
from services.producto_service import (
    obtener_productos,
    insertar_producto,
    obtener_producto,
    actualizar_producto,
    eliminar_producto
)

app = Flask(__name__)
app.secret_key = "clave_secreta"

# =========================
# LOGIN CONFIG
# =========================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# =========================
# MODELO USUARIO
# =========================

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
    user = cursor.fetchone()
    conexion.close()

    if user:
        return Usuario(user[0], user[1], user[2], user[3])
    return None

# =========================
# RUTAS PRINCIPALES
# =========================

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


# 🔥 PANEL CORREGIDO (IMPORTANTE)
@app.route('/panel')
@login_required
def panel():
    return render_template('panel.html')


@app.route('/factura')
@login_required
def factura():
    return render_template('factura.html')


@app.route('/clientes')
@login_required
def clientes():
    return render_template('clientes.html')

# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute(
                "SELECT * FROM usuarios WHERE email=%s AND password=%s",
                (email, password)
            )

            user = cursor.fetchone()
            conexion.close()

            if user:
                usuario = Usuario(user[0], user[1], user[2], user[3])
                login_user(usuario)
                return redirect(url_for('panel'))

            return "Credenciales incorrectas"

        except Exception as e:
            return f"Error: {e}"

    return render_template('login.html')

# =========================
# REGISTRO
# =========================

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('panel'))

    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
            existente = cursor.fetchone()

            if existente:
                conexion.close()
                return "El correo ya existe"

            cursor.execute(
                "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
                (nombre, email, password)
            )

            conexion.commit()
            conexion.close()

            return redirect(url_for('login'))

        except Exception as e:
            return f"Error: {e}"

    return render_template('registro.html')

# =========================
# LOGOUT
# =========================

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# =========================
# PRODUCTOS CRUD
# =========================

@app.route('/productos')
@login_required
def productos():
    try:
        datos = obtener_productos()
        return render_template('productos/listar.html', productos=datos)
    except Exception as e:
        return f"Error: {e}"


@app.route('/productos/agregar', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre'].strip()
            cantidad = int(request.form['cantidad'])
            precio = float(request.form['precio'])

            insertar_producto(nombre, cantidad, precio)

            return redirect(url_for('productos'))

        except Exception as e:
            return f"Error: {e}"

    return render_template('productos/agregar.html')


@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    if request.method == 'POST':
        try:
            nombre = request.form['nombre'].strip()
            cantidad = int(request.form['cantidad'])
            precio = float(request.form['precio'])

            actualizar_producto(id, nombre, cantidad, precio)

            return redirect(url_for('productos'))

        except Exception as e:
            return f"Error: {e}"

    producto = obtener_producto(id)
    return render_template('productos/editar.html', producto=producto)


@app.route('/productos/eliminar/<int:id>')
@login_required
def eliminar_producto_route(id):
    try:
        eliminar_producto(id)
        return redirect(url_for('productos'))
    except Exception as e:
        return f"Error: {e}"

# =========================
# REPORTE PDF
# =========================

@app.route('/reporte')
@login_required
def reporte():
    try:
        datos = obtener_productos()

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt="REPORTE DE PRODUCTOS", ln=True)

        pdf.set_font("Arial", size=12)

        for p in datos:
            pdf.cell(200, 8, txt=f"ID: {p[0]} | {p[1]} | Cantidad: {p[2]} | Precio: ${p[3]}", ln=True)

        pdf_output = pdf.output(dest='S').encode('latin-1')

        return send_file(
            io.BytesIO(pdf_output),
            download_name="reporte_productos.pdf",
            as_attachment=True
        )

    except Exception as e:
        return f"Error: {e}"

# =========================
# EJECUTAR
# =========================

if __name__ == '__main__':
    app.run(debug=True)