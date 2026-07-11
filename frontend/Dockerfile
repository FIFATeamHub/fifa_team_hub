    FROM node:22-alpine AS build

    WORKDIR /app
    
    # Instala dependências primeiro (aproveita cache de layers)
    COPY package.json package-lock.json ./
    RUN npm ci
    
    COPY . .
    
    # Variável de build-time: URL pública do backend no Cloud Run
    ARG VITE_API_URL
    ENV VITE_API_URL=${VITE_API_URL}
    
    RUN npm run build
    
    FROM nginx:alpine
    
    # Template do nginx (usa envsubst para injetar $PORT em runtime)
    COPY nginx.conf.template /etc/nginx/templates/default.conf.template
    
    # Copia os assets estáticos gerados no build
    COPY --from=build /app/dist /usr/share/nginx/html
    
    # Cloud Run injeta PORT dinamicamente; default 8080 para rodar local
    ENV PORT=8080
    EXPOSE 8080
    
    CMD ["/bin/sh", "-c", "envsubst '$PORT' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
