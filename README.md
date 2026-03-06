# Fix Manager

Fix Manager es una aplicación web ligera diseñada para la gestión de servicios técnicos y reparaciones. Permite el registro de órdenes de servicio, seguimiento de estados, asignación de técnicos y control financiero de costos y abonos.

## Características Principales
- **Gestión de Órdenes:** Registro de clientes, equipos y fallas.
- **Control Financiero:** Edición de costos totales y abonos adicionales.
- **Cierre Automático:** Al entregar el equipo, el saldo pendiente se ajusta a $0 de forma automática.
- **Roles:** Soporte para Administradores y Técnicos.

---

## Pasos para la Ejecución

Sigue estos pasos para configurar el entorno y poner en marcha la aplicación en tu máquina local.

### 1. Preparar el Entorno Virtual (venv)

Abre una terminal en la carpeta raíz del proyecto (`FixManager`) y ejecuta:

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate

```

**En Linux/macOS/WSL:**

```bash
python3 -m venv venv
source venv/bin/activate

```

### 2. Instalar Dependencias

Una vez activado el entorno virtual, instala las librerías necesarias:

```bash
pip install -r requirements.txt

```

### 3. Ejecutar la Aplicación

Para iniciar el servidor en el host local (`127.0.0.1`) y el puerto (`8000`), simplemente ejecuta el archivo de arranque:

```bash
python run.py

```

### 4. Acceso al Sistema

Una vez que el servidor esté corriendo, abre tu navegador y dirígete a:

* **URL:** [http://127.0.0.1:8000](https://www.google.com/search?q=http://127.0.0.1:8000)

### 5. Salir del entorno

Cuando termines de testear y/o trabajar, puedes desactivar el entorno con:

```bash
deactivate

```

---

## Estructura del Proyecto

* `run.py`: Script de arranque del servidor.
* `app/main.py`: Lógica principal y rutas de la aplicación.
* `app/database.py`: Configuración de la base de datos y modelos.
* `app/templates/`: Vistas HTML (Jinja2).

```