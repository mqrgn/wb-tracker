# Используем полную версию, в ней уже есть многие зависимости, она ставится быстрее slim в итоге
FROM python:3.12-bullseye

# 1. Устанавливаем только самое необходимое для работы
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    netcat \
    --no-install-recommends

# 2. Установка Chrome через официальный репозиторий (это быстрее и стабильнее)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 3. Сначала копируем только requirements и ставим их
# Это позволит не переустанавливать библиотеки, если ты меняешь только код бота
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. В самом конце копируем код проекта
COPY . .

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]