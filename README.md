# SistemaPMV

SistemaPMV es una aplicación de gestión de inventario orientada a pequeños y medianos almacenes de calzado. El sistema busca ofrecer una solución accesible para negocios que no cuentan con el presupuesto necesario para implementar plataformas empresariales costosas o servicios en la nube.

La aplicación permite administrar productos, empleados y futuras funcionalidades relacionadas con ventas, autenticación y control de inventario, utilizando tecnologías locales y de fácil implementación.

El proyecto está siendo desarrollado como parte del proceso formativo ADSO del SENA, aplicando buenas prácticas de organización de código, control de versiones con Git y trabajo colaborativo mediante GitHub.

---

# Objetivo del proyecto

Desarrollar un sistema modular, económico y fácil de implementar que permita:

- Gestionar productos de almacenes de calzado
- Administrar empleados
- Implementar autenticación de usuarios
- Organizar inventario de manera local y eficiente
- Escalar futuras funcionalidades como clientes, ventas, facturación y reportes.

---
# Stack tecnológico 

| Tecnología | Justificación |
|---|---|
| Python | Permite desarrollar aplicaciones rápidas, modulares y fáciles de mantener. |
| Tkinter | Facilita la creación de interfaces gráficas locales sin depender de tecnologías web. |
| MongoDB | Base de datos NoSQL flexible y ligera para gestionar inventario y usuarios. |
| PyMongo | Permite integrar Python con MongoDB de manera sencilla. |
| Git | Control de versiones para seguimiento del desarrollo. |
| GitHub | Trabajo colaborativo y respaldo del proyecto. |
| Visual Studio Code | Entorno de desarrollo utilizado por el equipo. |

---

# Características principales

- Interfaz gráfica desarrollada con Tkinter.
- Base de datos MongoDB.
- CRUD completo de productos.
- CRUD completo de empleados.
- Sistema de autenticación de usuarios.
- Arquitectura modular por capas.
- Persistencia local de datos.
- Control de versiones mediante Git y GitHub.

---
# Descripción de componentes

El sistema se encuentra organizado mediante una arquitectura modular por capas:

## UI

Gestiona la interfaz gráfica del sistema, ventanas, formularios y eventos del usuario.

## Services

Contiene la lógica de negocio y comunicación entre la interfaz y la base de datos.

## Models

Representa las entidades principales del sistema como productos y empleados.

## Database

Centraliza la conexión con MongoDB mediante PyMongo.

---

# Flujo general del sistema

```text
Usuario
    │
    ▼
Inicio de sesión
    │
    ▼
Menú principal
    │
 ┌──┴───────────┐
 ▼              ▼
Productos   Empleados
    │
    ▼
Services
    │
    ▼
MongoDB
```

# Estructura del proyecto

```text
SistemaPMV/
│
├── Assets/
│
├── database/
│   └── conexion.py
│
├── docs/
│   ├── login.png
│   ├── login1.png
│   ├── productos.png
│   ├── empleados.png
│   ├── commits_productos.png
│   └── commits_empleados.png
│
├── models/
│   ├── empleado.py
│   └── producto.py
│
├── services/
│   ├── empleado_service.py
│   └── producto_service.py
│
├── ui/
│   ├── login_window.py
│   ├── main_window.py
│   ├── ui_empleados.py
│   └── ui_productos.py
│
├── .gitignore
├── app.py
└── README.md
```

---

# Funcionalidades implementadas

- Sistema de autenticación mediante inicio de sesión.
- CRUD completo de productos.
- CRUD completo de empleados.
- Persistencia de datos con MongoDB.
- Arquitectura modular.
- Interfaz gráfica desarrollada con Tkinter.
- Trabajo colaborativo mediante Git y GitHub.

---

# Acceso al sistema

Para ingresar al sistema utilice las siguientes credenciales iniciales:

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | admin | 1234 |

---

# Instalación del proyecto

## 1. Clonar el repositorio

```bash
git clone https://github.com/fperdomo161dev-design/SistemaPMV.git
```

---

## 2. Entrar al proyecto

```bash
cd SistemaPMV
```

---

## 3. Instalar dependencias

```bash
pip install pymongo
```

---

# Configuración de MongoDB

## Instalación de MongoDB

### 1. Descargar MongoDB Community Server

Descargar MongoDB desde el sitio oficial:

https://www.mongodb.com/try/download/community

---

### 2. Instalar MongoDB

Durante la instalación se recomienda:

- Seleccionar instalación `Complete`
- Instalar MongoDB Compass
- Mantener MongoDB como servicio de Windows

---

### 3. Verificar instalación

Abrir PowerShell o CMD y ejecutar:

```bash
mongosh
```

Si MongoDB está funcionando correctamente, se abrirá la consola interactiva.

---

# Instalación de MongoDB Database Tools

El proyecto utiliza MongoDB Database Tools para exportar e importar la base de datos.

Carpeta utilizada:

```text
mongodb-database-tools-windows-x86_64-100.14.0
```

Las herramientas pueden descargarse desde:

https://www.mongodb.com/try/download/database-tools

---

# Base de datos utilizada

Nombre de la base de datos:

```text
zapateria_pmv
```

Cadena de conexión utilizada:

```python
MongoClient("mongodb://localhost:27017/")
```

---

# Restaurar base de datos

El proyecto incluye un archivo `.rar` que contiene:

- Backup de la base de datos `zapateria_pmv`
- Carpeta `mongodb-database-tools-windows-x86_64-100.14.0`

## 1. Descomprimir el archivo RAR

Extraer el contenido del archivo en cualquier ubicación del computador.

---

## 2. Abrir terminal dentro de MongoDB Database Tools

Ubicarse dentro de la carpeta `bin`:

```bash
cd mongodb-database-tools-windows-x86_64-100.14.0\bin
```

---

## 3. Restaurar la base de datos

Ejecutar:

```bash
mongorestore --db zapateria_pmv "ruta\\zapateria_pmv"
```

Ejemplo:

```bash
mongorestore --db zapateria_pmv "C:\\Users\\User\\Desktop\\zapateria_pmv"
```

---

## 4. Verificar restauración

Abrir Mongo Shell:

```bash
mongosh
```

Luego ejecutar:

```javascript
show dbs
use zapateria_pmv
show collections
```

---

# Ejecución del proyecto

⚠ Antes de ejecutar el sistema asegúrese de que MongoDB esté iniciado.

Para ejecutar la aplicación:

```bash
python app.py
```

---

# Flujo de trabajo con Git

## Actualizar proyecto

```bash
git pull origin main
```

---

## Guardar cambios

```bash
git add .
git commit -m "descripcion del cambio"
```

---

## Subir cambios

```bash
git push origin main
```

---

# Evidencia funcional

El proyecto cuenta actualmente con las siguientes funcionalidades implementadas:

- Sistema de autenticación mediante inicio de sesión.
- CRUD completo de productos.
- CRUD completo de empleados.
- Persistencia de datos utilizando MongoDB.
- Arquitectura modular.
- Control de versiones mediante Git y GitHub.

## Capturas del sistema

---

## Login principal

![Login](docs/login.png)
---

## Validación de acceso

![Login1](docs/login1.png)


---
## Gestión de Productos

El módulo permite:

- Registrar productos.
- Buscar por referencia.
- Actualizar productos.
- Eliminar productos.
- Visualizar registros en tabla.

![Productos](docs/productos.png)
---
## Gestión de Empleados

El módulo permite:

- Registrar empleados.
- Buscar por cédula.
- Actualizar empleados.
- Eliminar empleados.
- Visualizar registros en tabla.

![Empleados](docs/empleados.png)

---


## Trabajo colaborativo

![Productos](docs/commits_productos.png)

![Empleados](docs/commits_empleados.png)

---

# Recursos adicionales

El proyecto incluye:

- Backup de la base de datos
- MongoDB Database Tools
- Video explicativo de instalación y funcionamiento
- Evidencias visuales del sistema

---

# Integrantes

- Fredy Perdomo
- Yovanna Rodríguez

---


# Estado del proyecto

## Funcionalidades completadas

- Inicio de sesión.
- CRUD completo de productos.
- CRUD completo de empleados.
- Persistencia de datos con MongoDB.
- Arquitectura modular.
- Control de versiones mediante Git y GitHub.

---

## Próximas funcionalidades

- Gestión de clientes.
- Registro de ventas.
- Facturación.
- Reportes.
- Dashboard.
- Control avanzado de inventario.