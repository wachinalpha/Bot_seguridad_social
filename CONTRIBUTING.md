# 🤝 Guía para Colaboradores

¡Gracias por querer ayudar! Esta guía te explica paso a paso cómo contribuir al proyecto, incluso si es tu primera vez.

---

## 📋 Antes de empezar

### 1. Configurá tu entorno

Si todavía no instalaste el proyecto, seguí los pasos del [README](README.md).

### 2. Elegí una tarea

Mirá el archivo [TAREAS.md](TAREAS.md) para ver qué cosas hay pendientes. Las tareas están clasificadas por dificultad:
- 🟢 **Fácil** - Ideal para empezar
- 🟡 **Medio** - Requiere algo de experiencia
- 🔴 **Difícil** - Para desarrolladores con experiencia

---

## 🔄 Cómo proponer cambios (Pull Request)

Un "Pull Request" (PR) es la forma de proponer tus cambios al proyecto. Acá te explico cómo hacerlo paso a paso:

### Paso 1: Creá una rama nueva

Nunca trabajes directamente en `main`. Creá una rama con un nombre descriptivo:

```bash
# Primero asegurate de estar en main y actualizado
git checkout main
git pull

# Creá tu rama
git checkout -b agregar-nueva-feature
```

**Ejemplos de nombres de rama:**
- `fix-error-path`
- `agregar-documento-anses`
- `mejorar-readme`

### Paso 2: Hacé tus cambios

Editá los archivos que necesites. Probá que todo funcione antes de continuar.

### Paso 3: Guardá tus cambios (commit)

```bash
# Ver qué archivos cambiaste
git status

# Agregar todos los cambios
git add .

# Crear el commit con un mensaje descriptivo
git commit -m "Agrego nueva funcionalidad X"
```

**Tips para mensajes de commit:**
- Empezá con un verbo: "Agrego", "Corrijo", "Mejoro", "Elimino"
- Sé específico: "Corrijo error de encoding en Windows" es mejor que "Fix bug"

### Paso 4: Subí tu rama a GitHub

```bash
git push origin agregar-nueva-feature
```

### Paso 5: Creá el Pull Request

1. Andá a GitHub y abrí el repositorio
2. Va a aparecer un botón amarillo que dice **"Compare & pull request"** - hacé click
3. Completá el formulario:
   - **Título**: Descripción corta de qué hiciste
   - **Descripción**: Explicá qué cambiaste y por qué
4. Hacé click en **"Create pull request"**

### Paso 6: Esperá la revisión

Alguien del equipo va a revisar tu código. Pueden pasar 3 cosas:
- ✅ **Aprobado**: Tu código se fusiona con `main`
- 💬 **Comentarios**: Te piden que cambies algo. Hacé los cambios, commit y push de nuevo (el PR se actualiza solo)
- ❌ **Rechazado**: No te preocupes, te van a explicar por qué y podés intentar de nuevo

---

## 🧑‍💻 Configuración del entorno de desarrollo

### Estructura del proyecto

```
Bot_seguridad_social/
├── rag_app/          ← Backend (Python/FastAPI)
│   ├── adapters/     ← Conexiones con servicios externos
│   ├── services/     ← Lógica de negocio
│   └── api_main.py   ← Punto de entrada de la API
├── front/            ← Frontend (React)
└── docs/             ← Documentación técnica
```

### Ejecutar tests

```bash
cd rag_app
pytest tests/
```

### Formatear código

Antes de hacer commit, formateá tu código:

```bash
# Python
black rag_app/

# Ver errores de estilo
flake8 rag_app/
```

---

## 🌟 Buenas prácticas

### Código
- Escribí nombres de variables y funciones en español o inglés, pero sé consistente
- Agregá comentarios explicando el "por qué", no el "qué"
- Si algo es confuso, probablemente lo sea para otros también - simplificalo

### Comunicación
- Si tenés dudas, preguntá. No hay preguntas tontas
- Si algo no funciona, contá qué intentaste antes de pedir ayuda
- Celebrá los logros de otros 🎉

### Código de conducta
- Tratamos a todos con respeto
- Priorizamos la colaboración sobre la competencia
- Aceptamos que todos cometemos errores y aprendemos de ellos

---

## 🔒 Seguridad

- **Nunca subas tu archivo `.env`** con las API keys
- Si encontrás una vulnerabilidad de seguridad, no la publiques como issue. Contactá directamente al equipo.

---

## ❓ ¿Preguntas?

- Revisá el [README](README.md) y las [Preguntas Frecuentes](FAQ.md)
- Abrí un Issue en GitHub
- Preguntá en el grupo del equipo

¡Gracias por contribuir! 🚀
