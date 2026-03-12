# Stage 1: build
FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NODE_OPTIONS=--max-old-space-size=4096

RUN npm run build

# Stage 2: serve with nginx
FROM nginx:alpine

# Next.js static export outputs to out/
COPY --from=builder /app/out /usr/share/nginx/html

# SPA fallback: serve index.html for client-side routes
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { try_files $uri $uri/ /index.html; } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
