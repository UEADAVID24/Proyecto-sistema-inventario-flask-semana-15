# 🏪 Sistema Avanzado de Gestión de Inventario – Flask

## 📌 Descripción del Proyecto

Este proyecto consiste en el desarrollo de un **Sistema Avanzado de Gestión de Inventario** utilizando Flask, como evolución de las semanas anteriores.

El sistema permite gestionar productos mediante operaciones CRUD (Crear, Leer, Actualizar y Eliminar), integrando autenticación de usuarios, conexión a base de datos MySQL y generación de reportes en PDF.

Se aplicó una arquitectura por capas (models, services, forms) para organizar el código de manera modular y profesional.

---

## 🎯 Objetivos

* Implementar un sistema web con operaciones CRUD completas.
* Integrar una base de datos relacional (MySQL).
* Aplicar Programación Orientada a Objetos (POO).
* Organizar el proyecto en capas (models, services, forms).
* Implementar autenticación de usuarios (login y registro).
* Generar reportes en PDF desde la aplicación.
* Diseñar una interfaz web utilizando Jinja2 y Bootstrap.

---

## ⚙️ Tecnologías Utilizadas

* Python 3
* Flask
* MySQL
* HTML + Jinja2
* Bootstrap 5
* FPDF
* Git y GitHub
* Visual Studio Code

---

## 🏗️ Estructura del Proyecto

```
Mi_proyecto_flask_Clinton_Alvarado_semana15/
│
├── app.py
├── Conexion/
│   └── conexion.py
│
├── models/
│   └── producto.py
│
├── services/
│   └── producto_service.py
│
├── forms/
│   └── producto_form.py
│
├── templates/
│   ├── base.html
│   ├── panel.html
│   └── productos/
│       ├── listar.html
│       ├── agregar.html
│       └── editar.html
│
├── static/
│   └── styles.css
│
├── desarrollo_web.sql
└── README.md
```

---

## 🗄️ Base de Datos MySQL

El sistema utiliza una base de datos MySQL con las siguientes tablas:

* **productos**
* **clientes**
* **facturas**

Las tablas están relacionadas mediante claves foráneas (FOREIGN KEY).

El archivo `desarrollo_web.sql` contiene la estructura completa de la base de datos.

---

## 🔐 Autenticación de Usuarios

El sistema incluye:

* Registro de usuarios
* Inicio de sesión
* Cierre de sesión
* Protección de rutas con `login_required`

---

## 🔄 Operaciones CRUD

El sistema permite realizar:

* **Crear:** Agregar nuevos productos
* **Leer:** Visualizar productos en tabla
* **Actualizar:** Editar productos existentes
* **Eliminar:** Eliminar productos con confirmación

---

## 📄 Generación de Reportes

Se implementa la generación de reportes en PDF utilizando la librería **FPDF**.

El reporte incluye:

* Listado de productos
* Información clara y organizada

---

## 🖥️ Interfaz de Usuario

La aplicación cuenta con:

* Panel principal (dashboard)
* Navegación mediante navbar
* Formularios web
* Tablas dinámicas
* Estilos con Bootstrap

---

## 🚀 Ejecución del Proyecto

1️⃣ Instalar dependencias

```
pip install -r requirements.txt
```

2️⃣ Configurar la base de datos MySQL

Importar el archivo:

```
desarrollo_web.sql
```

3️⃣ Ejecutar la aplicación

```
py app.py
```

4️⃣ Abrir en el navegador

```
http://127.0.0.1:5000
```

---

## 👨‍💻 Autor

**Clinton David Alvarado Chongo**

Proyecto académico – Desarrollo de aplicaciones web con Flask 🚀
