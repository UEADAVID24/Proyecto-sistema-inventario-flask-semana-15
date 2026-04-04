from Conexion.conexion import obtener_conexion

def obtener_ventas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT 
            v.id,
            v.usuario_id,
            v.producto_id,
            v.cantidad,
            v.fecha,
            c.nombre,
            v.precio
        FROM ventas v
        JOIN clientes c ON v.cliente_id = c.id_cliente
    """)

    ventas = cursor.fetchall()
    conexion.close()
    return ventas