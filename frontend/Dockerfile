FROM node:22

WORKDIR /app

# Копируем package.json и package-lock.json (если есть)
COPY package*.json ./

# Устанавливаем зависимости через npm
RUN npm install

# Копируем весь проект
COPY . .

# Открываем порт Vite (обычно 5173)
EXPOSE 5173

# Запускаем dev сервер через npm
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]