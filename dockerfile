# Use uma imagem base Python
FROM python:3.11-slim

# Define o diretório de trabalho como /app/create-apis-base-unica
WORKDIR /app/create-apis-base-unica

# Copia o requirements.txt para o diretório /app/create-apis-base-unica/app no contêiner
COPY app/requirements.txt app/

# Instala o pip e as dependências do requirements.txt diretamente
RUN python -m pip install --upgrade pip && \
    pip install -r app/requirements.txt psycopg2-binary

# Copia todo o conteúdo do diretório local para o diretório /app/create-apis-base-unica no contêiner
COPY . .

# Expõe a porta 5002
EXPOSE 5002

# Com SSH
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "--reload", "app:create_app()"]

# Com WSL
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "app:app"]
