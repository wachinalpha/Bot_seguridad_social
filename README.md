# 🤖 Bot de Seguridad Social Argentina

Un asistente virtual que responde preguntas sobre jubilaciones y seguridad social en Argentina, usando inteligencia artificial.

---

## ¿Qué hace este proyecto?

Este bot lee documentos legales (como leyes de ANSES) y puede responder preguntas como:
- *"¿Cuáles son los requisitos para jubilarme?"*
- *"¿Qué es la moratoria previsional?"*
- *"¿Qué documentos necesito para tramitar la jubilación?"*

**Tecnología:** Usa un sistema llamado RAG (Retrieval Augmented Generation) que combina búsqueda de documentos con inteligencia artificial (Google Gemini).

---

## 🚀 Instalación Rápida (5 minutos)

### Paso 1: Requisitos previos

Necesitás tener instalado:
- **Python 3.13** o superior ([descargar](https://www.python.org/downloads/))
- **Node.js 18** o superior ([descargar](https://nodejs.org/))
- **Git** ([descargar](https://git-scm.com/))

### Paso 2: Clonar el proyecto

Abrí una terminal y ejecutá:

```bash
git clone https://github.com/tu-usuario/Bot_seguridad_social.git
cd Bot_seguridad_social
```

### Paso 3: Configurar el Backend (Python)

```bash
# Ir a la carpeta del backend
cd rag_app

# Crear archivo de configuración
# En Windows:
copy .env.example .env

# En Mac/Linux:
cp .env.example .env
```

Ahora abrí el archivo `.env` con cualquier editor y pegá tu API Key de Google Gemini:
```
GEMINI_API_KEY=tu_api_key_aqui
```

> 💡 **¿No tenés API Key?** Conseguila gratis en [Google AI Studio](https://aistudio.google.com/app/apikey)

Instalá las dependencias:
```bash
# Volver a la raíz del proyecto
cd ..

# Instalar dependencias de Python
.\.venv\Scripts\python.exe -m pip install -r rag_app/requirements.txt
```

### Paso 4: Configurar el Frontend (React)

```bash
cd front
npm install
```

### Paso 5: Cargar los documentos legales

Esto solo hay que hacerlo una vez. Carga los documentos de ANSES en la base de datos:

```bash
cd ..
# En Windows (PowerShell):
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m rag_app.scripts.setup_from_md
```

---

## ▶️ ¿Cómo ejecutar el bot?

Necesitás **2 terminales** abiertas al mismo tiempo:

### Terminal 1: Backend
```bash
cd rag_app
.\.venv\Scripts\python.exe api_main.py
```
Va a aparecer un mensaje diciendo que está corriendo en `http://localhost:8000`

### Terminal 2: Frontend
```bash
cd front
npm run dev
```
Va a aparecer un mensaje con la URL, normalmente `http://localhost:5173`

**¡Listo!** Abrí esa URL en tu navegador y empezá a chatear. 🎉

---

## 📝 ¿Cómo contribuir?

Si querés ayudar con el proyecto, leé la [Guía para Colaboradores](CONTRIBUTING.md).

Ahí vas a encontrar:
- Cómo configurar tu entorno de desarrollo
- Cómo proponer cambios (hacer un Pull Request)
- Lista de tareas disponibles para agarrar

---

## ❓ Preguntas Frecuentes

### El bot me dice "File path not found"

Esto pasa cuando la base de datos tiene rutas viejas. Solución:

```powershell
# En PowerShell:
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m rag_app.scripts.reset_db --force
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m rag_app.scripts.setup_from_md
```

### El comando `python` no funciona

En Windows, usá el Python del entorno virtual directamente:
```powershell
.\.venv\Scripts\python.exe -m tu_comando
```

### ¿Puedo agregar más documentos legales?

Sí. Poné tus archivos `.md` en la carpeta `Documentos_Anses/` y ejecutá el script de setup nuevamente.

---

## 📚 Documentación Técnica

Si sos desarrollador senior o querés entender cómo funciona por dentro, mirá:
- [Arquitectura Técnica](docs/TECNICO.md) - Cómo está construido el sistema
- [Documentación de la API](rag_app/docs/API.md) - Endpoints disponibles

---

## 📄 Licencia

Este proyecto es open source bajo licencia MIT. Podés usarlo, modificarlo y distribuirlo libremente.

---

**¿Dudas?** Abrí un [Issue en GitHub](https://github.com/tu-usuario/Bot_seguridad_social/issues) o preguntá en el grupo del equipo.
