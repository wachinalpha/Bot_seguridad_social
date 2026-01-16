# Security Policy

## Supported Versions

Las siguientes versiones del Bot de Seguridad Social están actualmente soportadas con actualizaciones de seguridad:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

La seguridad de nuestros usuarios es nuestra máxima prioridad. Si descubrís una vulnerabilidad de seguridad, por favor seguí estos pasos:

### 🔒 Reporte Privado (Recomendado)

**NO** abras un issue público para vulnerabilidades de seguridad.

En su lugar:

1. **Email**: Enviá un email a los mantenedores con:
   - Descripción detallada de la vulnerabilidad
   - Pasos para reproducir el problema
   - Impacto potencial
   - Sugerencias de mitigación (si las tenés)

2. **GitHub Security Advisory**: Usá la función de [Security Advisories](https://github.com/tu-usuario/Bot_seguridad_social/security/advisories) de GitHub

### ⏱️ Tiempo de Respuesta

- **Confirmación inicial**: Dentro de 48 horas
- **Evaluación**: Dentro de 7 días
- **Fix y disclosure**: Depende de la severidad (ver abajo)

### 📊 Niveles de Severidad

#### 🔴 Crítico
- Ejecución remota de código
- Acceso no autorizado a datos sensibles
- **Tiempo de fix**: 24-48 horas

#### 🟠 Alto
- Bypass de autenticación
- Inyección SQL/NoSQL
- **Tiempo de fix**: 7 días

#### 🟡 Medio
- Cross-Site Scripting (XSS)
- Exposición de información sensible
- **Tiempo de fix**: 30 días

#### 🟢 Bajo
- Problemas de configuración
- Mejoras de seguridad
- **Tiempo de fix**: 90 días

### 🎖️ Reconocimiento

Si reportás una vulnerabilidad válida:

- Tu nombre será incluido en el CHANGELOG (si lo deseás)
- Serás mencionado en el Security Advisory
- Agradecimiento público en la release notes

## 🛡️ Mejores Prácticas de Seguridad

### Para Usuarios

1. **API Keys**:
   - NUNCA commitees tu `GEMINI_API_KEY` al repositorio
   - Usá variables de entorno (`.env`)
   - Rotá las keys regularmente

2. **Deployment**:
   - Siempre usá HTTPS en producción
   - Configurá rate limiting
   - Implementá autenticación si es necesario

3. **Actualizaciones**:
   - Mantené las dependencias actualizadas
   - Revisá el CHANGELOG para security fixes

### Para Desarrolladores

1. **Código**:
   - Nunca loguees información sensible
   - Validá todos los inputs del usuario
   - Usá prepared statements para queries

2. **Dependencias**:
   - Ejecutá `npm audit` y `pip-audit` regularmente
   - Actualizá dependencias con vulnerabilidades conocidas

3. **Secrets**:
   - Usá `.env.example` para templates
   - Agregá `.env` al `.gitignore`
   - Considerá usar secret managers (AWS Secrets Manager, etc.)

## 🔍 Vulnerabilidades Conocidas

Actualmente no hay vulnerabilidades conocidas en la versión 0.1.0.

Revisá el [CHANGELOG](CHANGELOG.md) para historial de security fixes.

## 📚 Recursos

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [React Security Best Practices](https://react.dev/learn/security)

## 🤝 Política de Divulgación

Seguimos una política de **Responsible Disclosure**:

1. El reporter nos notifica en privado
2. Trabajamos en un fix
3. Publicamos el fix
4. Divulgamos la vulnerabilidad públicamente (con crédito al reporter)

**Tiempo típico**: 90 días desde el reporte inicial hasta la divulgación pública.

---

Gracias por ayudar a mantener seguro el Bot de Seguridad Social 🛡️
