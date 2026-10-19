# BibliotecaUN: préstamo y devolución de libros

Laboratorio 01 de Bases de Datos (202630). Aplicación web para gestionar el catálogo, los
ejemplares, los usuarios, los préstamos, las devoluciones con multa y los reportes de la
biblioteca de la universidad.

| Capa | Tecnología |
|---|---|
| Motor de base de datos | **MySQL 8** (GUI: MySQL Workbench) |
| Driver | `mysqlclient` (en `backend/requirements.txt`) |
| Backend (API REST) | Python + **Django** + Django REST Framework |
| Frontend | React + TypeScript (Vite) |

## Integrantes

| Nombre | Código |
|---|---|
| _Jefferson Jose Torres Lora_ | |
| _Maria Jose Sanchez Mercado_ | |
| _Natalia Paola Alvarado_ | |
| _Luis Alfonso Herrera_ | |
| _Eliud Quiroz_ | |
| _Yader Alejandro Vega Sabogal_ | |

## Contenido de la entrega

| Entregable | Dónde está |
|---|---|
| Diagrama entidad-relación (MER) | Anexo de la actividad |
| Diagrama relacional | Anexo de la actividad |
| Script de creación de tablas | [`scripts/Inicializacion.sql`](scripts/Inicializacion.sql) |
| Inserts de datos básicos | [`scripts/seed_datos.sql`](scripts/seed_datos.sql), [`scripts/seed_auth.sql`](scripts/seed_auth.sql), [`scripts/seed_prestamos.sql`](scripts/seed_prestamos.sql) |
| Archivos para ejecutar la aplicación | [`backend/`](backend) y [`frontend/`](frontend), con los pasos de abajo |

---

## Cómo ejecutarla en local

### Requisitos

- **MySQL 8.0.16 o superior**: el esquema usa restricciones `CHECK` y una columna generada.
- **Python 3.12 o superior**: lo exige Django 6.1.
- **Node.js 20.19+ o 22.12+**: lo exige Vite.

### 1. Crear la base de datos

Ejecuta los cuatro scripts **en este orden**, en MySQL Workbench o desde la terminal:

```bash
mysql -u root -p < scripts/Inicializacion.sql
```

```bash
mysql -u root -p < scripts/seed_datos.sql
```

```bash
mysql -u root -p < scripts/seed_auth.sql
```

```bash
mysql -u root -p < scripts/seed_prestamos.sql
```

| Script | Qué hace |
|---|---|
| `Inicializacion.sql` | Crea la BD `biblioteca` y sus 13 tablas, con la política de préstamo por rol y la tarifa de multa por día (1000). Borra las tablas si ya existían, así que se puede volver a ejecutar |
| `seed_datos.sql` | 10 editoriales, 8 categorías, autores, 30 libros, 93 ejemplares, 6 usuarios y 2 empleados |
| `seed_auth.sql` | Contraseñas de prueba (en la BD solo se guarda el hash) |
| `seed_prestamos.sql` | Préstamos de ejemplo, unos vigentes y otros vencidos, con fechas relativas a hoy |

No hace falta `manage.py migrate`: las tablas las crea el script, no Django.

### 2. Backend (Django)

```bash
cd backend
```

Crea y activa un entorno virtual. En Windows (PowerShell):

```bash
py -m venv .venv
```

```bash
.venv\Scripts\Activate.ps1
```

En macOS o Linux:

```bash
python3 -m venv .venv && source .venv/bin/activate
```

Instala las dependencias (en Linux, `mysqlclient` necesita antes `pkg-config` y `libmysqlclient-dev`):

```bash
pip install -r requirements.txt
```

Si `mysqlclient` no se deja instalar, usa esta lista en su lugar: trae PyMySQL, un driver en
Python puro que la app usa automáticamente cuando no encuentra `mysqlclient`:

```bash
pip install -r requirements-lambda.txt
```

Copia `backend/.env.example` como `backend/.env` y completa los valores. Para un MySQL local:

```ini
DB_NAME=biblioteca
DB_USER=root
DB_PASSWORD=<tu contraseña de MySQL>
DB_HOST=127.0.0.1
DB_PORT=3306
DB_SSL=false
SECRET_KEY=
```

`DB_SSL=false` desactiva la verificación con el certificado de AWS RDS, que un MySQL local no
tiene. En local `SECRET_KEY` puede quedar vacía: se usa una temporal y las sesiones se cierran al
reiniciar el servidor.

Levanta la API en http://localhost:8000:

```bash
python manage.py runserver
```

Para comprobarla, abre http://localhost:8000/api/auth/me/. Debe responder
`401 Las credenciales de autenticación no se proveyeron.`

### 3. Frontend (React)

En otra terminal:

```bash
cd frontend
```

```bash
npm install
```

Crea el archivo `frontend/.env.local` con esta línea (le dice al frontend dónde está la API):

```ini
VITE_API_URL=http://localhost:8000
```

Levanta la aplicación en http://localhost:5173:

```bash
npm run dev
```

### 4. Credenciales de prueba

| Cuenta | Correo | Contraseña |
|---|---|---|
| Administrador | `admin.biblioteca@uninorte.edu.co` | `Admin123!` |
| Bibliotecario | `bibliotecario@uninorte.edu.co` | `Usuario123!` |
| Estudiante | `majo@uninorte.edu.co` | `Usuario123!` |
| Docente | `rangulo@uninorte.edu.co` | `Usuario123!` |
| Estudiante bloqueado | `acastro@uninorte.edu.co` | `Usuario123!` (no puede entrar) |

### Pruebas automáticas (opcional)

```bash
cd backend && python manage.py test
```

Crean una BD temporal `test_biblioteca` con el mismo `Inicializacion.sql`, así que el usuario de
MySQL necesita permiso para crear bases de datos (por ejemplo `root` en local).

---

## Cómo se cumple cada requerimiento

| Requerimiento | Dónde se ve en la aplicación |
|---|---|
| CRUD de libros (ISBN, título, autores, editorial, año, categoría, descripción) | **Catálogo**: agregar, editar y retirar (el libro se oculta y su historial se conserva) |
| CRUD de ejemplares (código de barras, ubicación, estado) | **Ejemplares**: registrar, editar y dar de baja |
| Búsqueda por título, autor, ISBN, categoría y disponibilidad | **Catálogo**: filtros de búsqueda |
| CRUD de usuarios (código, identificación, nombres, correo, rol, carrera, estado) | **Usuarios** (administrador): registrar, editar, bloquear o desbloquear y eliminar |
| Historial de préstamos por usuario | **Usuarios** → *Ver préstamos*. Cada estudiante también ve el suyo en *Mis préstamos* |
| El usuario solicita el préstamo y el personal lo aprueba | El estudiante pulsa *Solicitar préstamo* en el **Catálogo**; el bibliotecario aprueba o rechaza en **Préstamos** |
| Validar usuario activo y ejemplar disponible | Al solicitar y otra vez al aprobar (`backend/prestamos/servicios.py`) |
| Devolución: el ejemplar vuelve a disponible, con observaciones | **Devoluciones**: condición (bueno o dañado) y observaciones, por ejemplo "páginas faltantes" |
| Multa automática por retraso, con tarifa por día | Se calcula al devolver: días de retraso × `tarifa_multa_dia` de la tabla `configuracion`. Se ven en **Multas** |
| Préstamos activos y vencidos | **Inicio** y **Reportes** |
| Libros más prestados por periodo, usuarios con más préstamos | **Reportes**, con filtro de fechas |
| Inventario por estado | **Ejemplares** (resumen) y **Reportes** |

## Estructura del repositorio

```
scripts/          Scripts SQL: creación de tablas y datos de prueba
backend/          API REST en Django, una app por módulo:
  catalogo/         libros, autores, editoriales, categorías y búsqueda
  ejemplares/       ejemplares e inventario
  usuarios/         usuarios, login con JWT y permisos por rol
  prestamos/        solicitud, aprobación y rechazo
  devoluciones/     devoluciones y multas
  reportes/         reportes y exportación a CSV
frontend/         Interfaz web en React
```
