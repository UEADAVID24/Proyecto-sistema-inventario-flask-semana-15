# services/producto_service.py

from Conexion.conexion import obtener_conexion

def obtener_productos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos")
    datos = cursor.fetchall()
    conexion.close()
    return datos


def insertar_producto(nombre, cantidad, precio):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "INSERT INTO productos (nombre, cantidad, precio) VALUES (%s, %s, %s)",
        (nombre, cantidad, precio)
    )

    conexion.commit()
    conexion.close()


def obtener_producto(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM productos WHERE id_producto=%s", (id,))
    producto = cursor.fetchone()

    conexion.close()
    return producto


def actualizar_producto(id, nombre, cantidad, precio):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE productos 
        SET nombre=%s, cantidad=%s, precio=%s 
        WHERE id_producto=%s
    """, (nombre, cantidad, precio, id))

    conexion.commit()
    conexion.close()


def eliminar_producto(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM productos WHERE id_producto=%s", (id,))
    conexion.commit()
    conexion.close()