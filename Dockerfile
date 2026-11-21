FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
FROM nginx:alpine
# O nginx substitui ${API_UPSTREAM} na inicialização (somente variáveis definidas).
ENV API_UPSTREAM=http://host.docker.internal:8000
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
