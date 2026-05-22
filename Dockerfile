# Usar una imagen oficial de Python ligera
FROM python:3.9-slim

# Evitar que Python escriba archivos .pyc y habilitar buffering de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo en el contenedor para coincidir con el disco persistente de Render
WORKDIR /opt/render/project/src

# Instalar dependencias del sistema si fueran necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Compilar todos los templates estáticos de Stitch/onboarding antes de iniciar
# (esto asegura que todo el frontend premium esté empaquetado para producción)
RUN python build_all_templates.py

# Exponer el puerto por defecto
EXPOSE 8501

# Comando por defecto para iniciar la aplicación (Render/Railway proveerán la variable PORT)
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8501}"]
