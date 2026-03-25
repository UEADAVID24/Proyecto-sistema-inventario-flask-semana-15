# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================

from flask import Flask, render_template, request, redirect, url_for, send_file
from Conexion.conexion import obtener_conexion
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from fpdf import FPDF
import io

# Importación de servicios (capa lógica)
from services.producto_service import (
    obtener_productos,
    insertar_producto,
    obtener_producto,
    actualizar_producto,
    eliminar_producto
)

# ==========================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ==========================================

app = Flask(__name__)
app.secret_key = "clave_secreta"  # Clave para sesiones

# ==========================================
# CONFIGURACIÓN DE LOGIN
# ==========================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirige al login si no está autenticado

# ==========================================
# MODELO DE USUARIO (POO)
# ==========================================

class Usuario(UserMixin):
    """
    Clase que representa un usuario del sistema.
    Se utiliza para manejar la autenticación con Flask-Login.
    """
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    """
    Carga un usuario desde la base de datos
    a partir de su ID (requerido por Flask-Login)
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
    user = cursor.fetchone()
    conexion.close()

    if user:
        return Usuario(user[0], user[1], user[2], user[3])
    return None

# ==========================================
# RUTAS PRINCIPALES
# ==========================================

@app.route('/')
def home():
    """Página principal"""
    return render_template('index.html')


@app.route('/about')
def about():
    """Página de información"""
    return render_template('about.html')


@app.route('/panel')
@login_required
def panel():
    """Panel principal del usuario"""
    return render_template('panel.html')


@app.route('/factura')
@login_required
def factura():
    """Vista de facturas"""
    return render_template('factura.html')


@app.route('/clientes')
@login_required
def clientes():
    """Vista de clientes"""
    return render_template('clientes.html')

# ==========================================
# AUTENTICACIÓN (LOGIN / REGISTRO)
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Permite a los usuarios iniciar sesión.
    Verifica credenciales en la base de datos.
    """
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


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    Permite registrar nuevos usuarios en el sistema.
    """
    if current_user.is_authenticated:
        return redirect(url_for('panel'))

    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Verificar si el usuario ya existe
            cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
            existente = cursor.fetchone()

            if existente:
                conexion.close()
                return "El correo ya existe"

            # Insertar nuevo usuario
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


@app.route('/logout')
@login_required
def logout():
    """Cerrar sesión del usuario"""
    logout_user()
    return redirect(url_for('login'))

# ==========================================
# CRUD DE PRODUCTOS
# ==========================================

@app.route('/productos')
@login_required
def productos():
    """Mostrar lista de productos"""
    try:
        datos = obtener_productos()
        return render_template('productos/listar.html', productos=datos)
    except Exception as e:
        return f"Error: {e}"


@app.route('/productos/agregar', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    """Agregar un nuevo producto"""
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
    """Editar un producto existente"""
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
    """Eliminar un producto"""
    try:
        eliminar_producto(id)
        return redirect(url_for('productos'))
    except Exception as e:
        return f"Error: {e}"

# ==========================================
# GENERACIÓN DE REPORTE PDF
# ==========================================

@app.route('/reporte')
@login_required
def reporte():
    """
    Genera un reporte en PDF con la lista de productos.
    """
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

# ==========================================
# EJECUCIÓN DE LA APLICACIÓN
# ==========================================

if __name__ == '__main__':
    app.run(debug=True)