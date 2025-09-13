# Usar una imagen base de Python
FROM python:3.10-slim

# Instalar uv, el instalador de paquetes de Python
RUN pip install uv

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de dependencias del proyecto
COPY pyproject.toml .

# Instalar dependencias usando uv.
# La opción --system instala los paquetes en el entorno global del contenedor.
RUN uv pip install --system .

# Copiar el código fuente de la aplicación
COPY ./src .

# Comando para ejecutar el scraper
CMD ["python", "scraper.py"]
