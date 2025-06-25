# Use uma imagem do Python
FROM python:3.10-slim

# Instale Wine para permitir a execução de executáveis do Windows
RUN apt-get update && apt-get install -y wine

# Instale o PyInstaller
RUN pip install pyinstaller

# Crie um diretório de trabalho
WORKDIR /app

# Copie seu script Python para o contêiner
COPY main.py .

# Crie o executável
CMD ["wine", "pyinstaller", "--onefile", "seu_script.py"]
