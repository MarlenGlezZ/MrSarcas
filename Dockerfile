FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear directorio para datos persistentes
RUN mkdir -p /app/data

# Copiar archivos de la aplicación
COPY bot.py .

# Establecer directorio de trabajo para los datos persistentes
VOLUME /app/data

# Configurar entrypoint
CMD ["python", "bot.py"]