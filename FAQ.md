# ❓ Preguntas Frecuentes

Respuestas rápidas a los problemas más comunes.

---

## Instalación

### "Python no encontrado" o "python was not found"

En Windows, usá el Python del entorno virtual directamente:

```powershell
.\.venv\Scripts\python.exe -m tu_comando
```

En lugar de:
```
python -m tu_comando  ← Esto NO funciona
```

### "uv no reconocido como comando"

Si no tenés `uv` instalado, no pasa nada. Usá pip directamente:

```powershell
.\.venv\Scripts\pip.exe install -r requirements.txt
```

---

## Errores al usar el bot

### "File path not found: /home/..." 

La base de datos tiene rutas de otra computadora. Reseteala:

```powershell
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m rag_app.scripts.reset_db --force
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m rag_app.scripts.setup_from_md
```

### El bot responde cosas raras cuando digo "Hola"

Es normal. El bot está diseñado para responder preguntas legales, no para charlar. Siempre busca un documento y responde basándose en él, incluso si solo decís "Hola".

Probá con preguntas específicas como:
- "¿Cuáles son los requisitos para jubilarse?"
- "¿Qué es la moratoria?"

### "Puerto 8000 ya en uso"

Otro programa está usando ese puerto. Podés:

1. Cerrar la otra terminal que esté corriendo el backend
2. O buscar y matar el proceso:

```powershell
# Ver qué usa el puerto
netstat -ano | findstr :8000

# Matar el proceso (reemplazá XXXX por el número de PID)
taskkill /PID XXXX /F
```

---

## API Key

### ¿Dónde consigo la API Key de Gemini?

1. Andá a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Logueate con tu cuenta de Google
3. Hacé click en "Create API Key"
4. Copiá la key y pegala en tu archivo `.env`

### ¿Es gratis?

Sí, hay un tier gratuito que alcanza para desarrollo y uso moderado. Si hacés muchas consultas, puede que necesites el plan pago.

---

## Git y GitHub

### ¿Qué es un Pull Request?

Es la forma de proponer tus cambios al proyecto. Mirá la [Guía para Colaboradores](CONTRIBUTING.md) donde te explicamos paso a paso cómo hacerlo.

### ¿Cómo actualizo mi copia local?

```bash
git checkout main
git pull origin main
```

---

## ¿Más dudas?

Abrí un [Issue en GitHub](https://github.com/tu-usuario/Bot_seguridad_social/issues) o preguntá en el grupo del equipo.
