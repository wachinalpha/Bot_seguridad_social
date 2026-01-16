# Preguntas Frecuentes (FAQ)

## 📋 Tabla de Contenidos

- [General](#general)
- [Instalación y Configuración](#instalación-y-configuración)
- [Uso y Funcionalidad](#uso-y-funcionalidad)
- [Desarrollo](#desarrollo)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## General

### ¿Qué es el Bot de Seguridad Social?

Es un asistente virtual basado en RAG (Retrieval Augmented Generation) que responde consultas sobre la seguridad social argentina utilizando documentos legales oficiales como fuente de información.

### ¿Qué tecnologías utiliza?

- **Backend**: Python 3.13+, FastAPI, Google Gemini API, ChromaDB
- **Frontend**: React 19, TypeScript, Vite
- **Arquitectura**: Hexagonal (Ports & Adapters)

### ¿Es gratuito?

El código es open source (MIT License). Sin embargo, necesitás una API key de Google Gemini:
- **Free Tier**: Funciona pero sin context caching (más lento)
- **Paid Tier**: Incluye context caching (más rápido y eficiente)

### ¿Puedo usar esto para otros dominios?

¡Sí! La arquitectura hexagonal permite adaptar fácilmente el sistema a otros dominios (leyes de otro país, documentación técnica, etc.) cambiando solo los documentos fuente.

---

## Instalación y Configuración

### ¿Necesito instalar Docker?

No es obligatorio. Podés ejecutar el proyecto directamente con Python y Node.js. Docker es opcional y recomendado para deployment.

### ¿Qué versión de Python necesito?

Python 3.13 o superior. Verificá con:
```bash
python --version
```

### ¿Cómo obtengo una API key de Gemini?

1. Ir a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Crear una nueva API key
3. Copiarla al archivo `.env`

### ¿Puedo usar OpenAI en lugar de Gemini?

Actualmente solo soportamos Gemini, pero la arquitectura permite agregar otros providers fácilmente. Ver [CONTRIBUTING.md](CONTRIBUTING.md) para detalles.

### Error: "GEMINI_API_KEY not found"

Asegurate de:
1. Crear el archivo `.env` en `rag_app/`
2. Agregar la línea: `GEMINI_API_KEY=tu_api_key_aqui`
3. Reiniciar el servidor

---

## Uso y Funcionalidad

### ¿Qué tipo de preguntas puedo hacer?

Cualquier consulta relacionada con seguridad social argentina:
- "¿Cuáles son los requisitos para jubilarme?"
- "¿Qué es la moratoria previsional?"
- "¿Cómo tramito la jubilación?"

### ¿Las respuestas son 100% precisas?

Las respuestas se basan en documentos legales oficiales, pero:
- ⚠️ El sistema puede cometer errores
- ⚠️ La información puede estar desactualizada
- ⚠️ Siempre verificá con fuentes oficiales para decisiones importantes

### ¿Puedo agregar más documentos?

Sí, hay dos formas:

**Opción 1: Desde archivo local**
```bash
# Copiar documento a Documentos_Anses/
# Ejecutar script de ingestion
python -m rag_app.scripts.setup_from_md
```

**Opción 2: Desde URL**
```bash
# Editar config/leyes_config.json
# Ejecutar script
python -m rag_app.scripts.setup_db
```

### ¿Soporta conversaciones multi-turno?

Sí, usando `session_id` en las requests:
```json
{
  "query": "¿Requisitos para jubilación?",
  "session_id": "mi-sesion-123"
}
```

---

## Desarrollo

### ¿Cómo contribuyo al proyecto?

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guía completa. En resumen:
1. Fork el repo
2. Crear rama de feature
3. Hacer cambios
4. Abrir Pull Request

### ¿Dónde están los tests?

En `rag_app/tests/`. Ejecutar con:
```bash
pytest rag_app/tests/
```

### ¿Cómo agrego un nuevo adapter?

Ver [DEVELOPMENT.md](DEVELOPMENT.md) sección "Arquitectura del Código" para ejemplos detallados.

### ¿Qué es la arquitectura hexagonal?

Patrón de diseño que separa:
- **Domain**: Lógica de negocio pura
- **Ports**: Interfaces/contratos
- **Adapters**: Implementaciones concretas
- **Services**: Orquestación

Beneficios: testeable, flexible, mantenible.

---

## Deployment

### ¿Cómo despliego en producción?

Ver [DEPLOYMENT.md](DEPLOYMENT.md) para guías completas de:
- Docker
- Google Cloud Run
- AWS ECS
- Railway/Render

### ¿Necesito HTTPS?

Sí, en producción siempre usá HTTPS para proteger las API keys y datos de usuarios.

### ¿Cómo escalo el sistema?

**Horizontal scaling:**
- Múltiples instancias del backend detrás de load balancer
- Usar PostgreSQL con pgvector en lugar de ChromaDB local

**Vertical scaling:**
- Aumentar recursos (CPU/RAM) del contenedor

### ¿Qué base de datos vectorial recomiendan para producción?

- **PostgreSQL + pgvector**: Para cargas medias, buena integración
- **Pinecone**: Para cargas altas, fully managed
- **Weaviate**: Open source, features avanzadas

---

## Troubleshooting

### El backend inicia pero no responde

**Verificar:**
1. ¿Hay documentos indexados?
   ```bash
   python -c "from rag_app.adapters.stores.chroma_adapter import ChromaAdapter; print(ChromaAdapter().count_documents())"
   ```
2. ¿Los logs muestran errores?
3. ¿La API key es válida?

### Error: "Port 8000 already in use"

**Solución Windows:**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Solución Linux/Mac:**
```bash
lsof -ti:8000 | xargs kill -9
```

### Frontend no se conecta al backend

**Verificar:**
1. Backend está corriendo en `http://localhost:8000`
2. CORS está configurado correctamente en `api_main.py`
3. `VITE_API_URL` en frontend apunta a la URL correcta

### Respuestas muy lentas

**Posibles causas:**
1. **Free Tier de Gemini**: Sin cache, cada query procesa documento completo
   - Solución: Upgrade a paid tier
2. **Documentos muy grandes**: 
   - Solución: Optimizar chunking
3. **Red lenta**:
   - Solución: Deployment más cercano al usuario

### Error: "ChromaDB lock"

**Solución:**
1. Detener todos los procesos que usan ChromaDB
2. Eliminar archivos de lock en `chroma_db/`
3. Reiniciar

### Error: "File path not found: /home/..."

**Causa:**
Esto ocurre si clonaste el repositorio con una base de datos vectorial pre-existente que tiene rutas de otra máquina.

**Solución:**
Necesitás resetear la base de datos para que guarde las rutas de tu máquina:

```powershell
# 1. Resetear DB (PowerShell)
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m rag_app.scripts.reset_db --force

# 2. Re-ingestar documentos
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m rag_app.scripts.setup_from_md
```

### Las respuestas no son precisas

**Verificar:**
1. ¿Los documentos fuente son correctos?
2. ¿El embedding model es apropiado?
3. ¿El prompt en `contextualizer` es claro?

**Mejorar:**
- Agregar más documentos relevantes
- Ajustar parámetros de búsqueda (top_k, threshold)
- Mejorar el prompt del LLM

---

## Performance

### ¿Cuánto cuesta usar Gemini?

**Free Tier:**
- 15 requests/minuto
- Sin context caching
- Gratis

**Paid Tier:**
- Sin límite de requests
- Context caching incluido
- ~$0.50 primera query, ~$0.05 queries subsecuentes (con cache)

### ¿Cuánto tiempo toma una query?

**Con cache (Paid):**
- Primera query: ~15 segundos
- Queries subsecuentes: ~2 segundos

**Sin cache (Free):**
- Todas las queries: ~15 segundos

### ¿Cuántos documentos puedo indexar?

**ChromaDB local:**
- Hasta ~10,000 documentos (depende de RAM)

**PostgreSQL + pgvector:**
- Millones de documentos

---

## Seguridad

### ¿Cómo protejo mi API key?

1. **Nunca** commitees `.env` al repositorio
2. Usá variables de entorno en producción
3. Rotá las keys regularmente
4. Considerá usar secret managers (AWS Secrets Manager, etc.)

### ¿Hay autenticación?

No por defecto. Para agregar autenticación ver [DEPLOYMENT.md](DEPLOYMENT.md) sección "Seguridad".

### ¿Cómo reporto una vulnerabilidad?

Ver [SECURITY.md](SECURITY.md) para política de seguridad y proceso de reporte.

---

## Más Preguntas?

- 📖 [Documentación Completa](README.md)
- 💬 [Abrir un Issue](https://github.com/tu-usuario/Bot_seguridad_social/issues)
- 🤝 [Guía de Contribución](CONTRIBUTING.md)
