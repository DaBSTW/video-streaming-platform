# Video Streaming Platform

Plataforma de streaming con panel administrativo y reproductor ArtPlayer

## Características

- **Panel Administrativo**: Interfaz para gestionar videos, usuarios y configuraciones
- **Subida de Videos**: Sistema de carga de videos con procesamiento en cloud
- **Reproductor ArtPlayer**: Integración completa con ArtPlayer para reproducción avanzada
- **Sistema de Embed**: Generación de códigos iframe para incrustar videos en otras webs
- **Base de Datos PostgreSQL**: Almacenamiento robusto y escalable
- **Cloud Storage**: Almacenamiento en la nube con CDN

## Tecnologías

### Backend
- Python 3.9+
- Flask
- PostgreSQL
- SQLAlchemy
- Flask-JWT-Extended
- Boto3 (AWS S3)
- Flask-CORS

### Frontend
- Vue.js 3
- Vite
- Vue Router
- Pinia (Store)
- Tailwind CSS
- ArtPlayer.js

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:
   ```bash
   npm run install:all
   ```
3. Configurar variables de entorno (ver `.env.example`)
4. Iniciar el desarrollo:
   ```bash
   npm run dev
   ```

## Estructura del Proyecto

```
video-streaming-platform/
├── backend/           # API Flask
├── frontend/          # Aplicación Vue.js
├── docs/             # Documentación
└── scripts/          # Scripts de utilidad
```

## Licencia

MIT"# video-streaming-platform" 
