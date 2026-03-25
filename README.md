# UTEZ · Solver web con Transformada de Laplace

Proyecto web en Flask para resolver ecuaciones diferenciales ordinarias de primer y segundo orden mediante transformada de Laplace.

## Qué incluye

- Captura de ecuaciones de primer y segundo orden.
- Condiciones iniciales `y(0)` y `y'(0)`.
- Transformada de la ecuación.
- Solución en el dominio de Laplace `Y(s)`.
- Solución final `y(t)`.
- Gráfica automática con Matplotlib.
- Tutorial inicial con botón **Omitir tutorial**.
- **Modo oscuro** persistente.
- **Modo IA** opcional con API de OpenAI.
- Persistencia local de datos con `localStorage`.
- Botón **Borrar contenido**.

## Estructura recomendada del proyecto

```text
utez_laplace_web/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── .gitignore
├── deployment/
│   └── pythonanywhere_wsgi_example.py
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── app.js
│   └── img/
│       └── logo_UTEZ.png
├── templates/
│   ├── base.html
│   ├── index.html
│   └── _tutorial.html
├── tests/
│   └── test_solver.py
└── utils/
    ├── __init__.py
    ├── ai_helper.py
    └── solver.py
```

## Instalación local en Visual Studio Code

1. Abre la carpeta del proyecto en VS Code.
2. Crea y activa un entorno virtual.
3. Instala dependencias.
4. Copia `.env.example` a `.env`.
5. Ejecuta la aplicación.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Luego abre:

```text
http://127.0.0.1:5000
```

## Formato sugerido de entrada

- `y' + 2y = 0`
- `y'' + 3y' + 2y = 0`
- `y' - y = e^t`
- `y'' + y = sin(t)`

## Casos de prueba mínimos

1. `y' + 2y = 0`, `y(0) = 1`
2. `y'' + 3y' + 2y = 0`, `y(0) = 0`, `y'(0) = 1`
3. `y' - y = e^t`, `y(0) = 1`
4. `y'' + y = sin(t)`, `y(0) = 0`, `y'(0) = 0`

## Cómo funciona el Modo IA

El switch **Modo IA** prepara la interfaz para pedir una explicación adicional del resultado. La llamada a OpenAI se hace **desde el servidor**, nunca desde el navegador.

### Variables necesarias

```env
OPENAI_API_KEY=tu_api_key
OPENAI_MODEL=gpt-5.4
```

## Despliegue en PythonAnywhere

### 1) Sube tu proyecto

Puedes comprimir la carpeta y subirla desde la pestaña **Files**, o usar Git.

### 2) Crea un virtualenv

Desde una consola Bash:

```bash
mkvirtualenv utezenv --python=/usr/bin/python3.13
workon utezenv
pip install -r /home/TU_USUARIO/utez_laplace_web/requirements.txt
```

> Cambia `TU_USUARIO` por tu nombre real de usuario en PythonAnywhere.

### 3) Crea la web app

- Ve a **Web**.
- Elige **Add a new web app**.
- Selecciona **Manual Configuration**.
- Selecciona la misma versión de Python que usaste en el virtualenv.
- En la sección **Virtualenv**, apunta a tu entorno.

### 4) Configura el archivo WSGI

Usa el ejemplo del archivo `deployment/pythonanywhere_wsgi_example.py` y ajusta rutas y usuario.

### 5) Configura archivos estáticos

Agrega el mapeo:

- URL: `/static/`
- Carpeta: `/home/TU_USUARIO/utez_laplace_web/static`

### 6) Carga variables de entorno

Crea un archivo `.env` dentro del proyecto y haz que el WSGI lo cargue.

### 7) Recarga la app

Haz clic en **Reload** desde la pestaña **Web**.

## Notas

- Si no configuras `OPENAI_API_KEY`, el proyecto sigue funcionando; solo se desactiva la explicación IA.
- Para nuevos formatos de ecuación, amplía la lógica en `utils/solver.py`.
