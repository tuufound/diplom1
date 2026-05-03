FROM node:22

WORKDIR /app

# Копируем package.json и package-lock.json (если есть)
COPY package*.json ./

# Устанавливаем зависимости через npm
RUN npm install

# Копируем весь проект
COPY . .

EXPOSE 3000

# Порт как в vite.config.js; --host для доступа с хоста и по LAN
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]