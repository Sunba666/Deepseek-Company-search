FROM node:20-slim
RUN apt-get update -qq && apt-get install -y -qq openssl ca-certificates --no-install-recommends && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY prisma/ ./prisma/
RUN npx prisma generate
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["node", "dist/main"]
