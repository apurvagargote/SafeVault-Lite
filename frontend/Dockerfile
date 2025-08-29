# Minimal build
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install --silent --no-audit --no-fund
COPY . .
RUN npm run build && rm -rf node_modules

# Ultra-minimal production
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
RUN echo 'server{listen 80;root /usr/share/nginx/html;index index.html;location /{try_files $uri $uri/ /index.html;}}' > /etc/nginx/conf.d/default.conf && \
    rm -rf /var/cache/nginx/* /etc/nginx/conf.d/default.conf.bak
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]