# Imagem para executar o projeto de ponta a ponta em qualquer máquina (Aula 2 de Ambientes)
# Construir: docker build -t case-nps .
# Executar:  docker run --rm case-nps
# (ao final, a imagem roda os 4 notebooks em ordem e pontua os pedidos com o modelo)

# Passo 1: imagem base oficial do Python, versão leve ("slim")
FROM python:3.13-slim

# Passo 2: diretório de trabalho dentro do container
WORKDIR /app

# Passo 3: copia APENAS o requirements.txt primeiro, para aproveitar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Passo 4: copia o restante do projeto
COPY . .

# Passo 5: comando padrão: executa os notebooks em ordem e depois pontua os pedidos
CMD ["sh", "-c", "jupyter nbconvert --to notebook --execute --inplace notebooks/0*.ipynb && python -m src.prever --entrada data/raw/desafio_nps_fase_1.csv --saida reports/pedidos_pontuados.csv"]
