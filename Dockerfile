# imagen base
FROM python:3.12-slim
# carpeta de trabajo dentro de la imagen
WORKDIR /app
# primero solo las dependencias...
COPY requirements.txt .            
RUN pip install --no-cache-dir -r requirements.txt
# ...y después el código
COPY . .                           
# lo que se ejecuta al arrancar el contenedor
CMD ["python3", "-m", "pytest"]          