# ---- build: instala dependências com o toolchain completo do Node ----
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

# ---- runtime: sem npm, sem shell, só o Node e o que ele precisa pra rodar ----
FROM gcr.io/distroless/nodejs20-debian12

WORKDIR /app

COPY --from=build /app/node_modules ./node_modules
COPY . .

EXPOSE 3000

CMD ["server.js"]
