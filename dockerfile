# Use uma imagem base Python
FROM python:3.11-slim

# Define o diretório de trabalho como /app/create-apis-base-unica
WORKDIR /app/create-apis-base-unica

# Instala o pacote venv para gerenciar ambientes virtuais
RUN python3 -m venv venv

# Copia todo o conteúdo do diretório local para o diretório /app/create-apis-base-unica no contêiner
COPY . .

# Copia o requirements.txt para o diretório /app/create-apis-base-unica/app no contêiner
COPY app/requirements.txt app/

# Ativa o ambiente virtual e instala as dependências do requirements.txt dentro de /app/create-apis-base-unica/app
RUN ./venv/bin/python -m pip install --upgrade pip && \
    ./venv/bin/python -m pip install -r app/requirements.txt psycopg2-binary watchdog

# Expõe a porta 5002
EXPOSE 5002

# com ssh
CMD ["./venv/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "--reload", "app:create_app()"]

# com wsl
# CMD ["./venv/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "app:app"]
