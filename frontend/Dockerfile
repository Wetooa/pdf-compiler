# Stage 1: build
FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

# Build-time API URL (override when running in Docker Compose / Coolify)
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Ensure non-empty and give Node more memory for the build (avoids OOM in CI/Coolify)
ENV NODE_OPTIONS=--max-old-space-size=4096
RUN export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000}" && npm run build

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
