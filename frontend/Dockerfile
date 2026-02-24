# ── Stage 1: Build ────────────────────────────────────────────
FROM node:22-slim AS builder

WORKDIR /app

COPY . .
RUN rm -rf node_modules package-lock.json && npm install && npm run build

# ── Stage 2: Serve with nginx ────────────────────────────────
FROM nginx:alpine

# Remove default nginx content
RUN rm -rf /usr/share/nginx/html/*

# Copy built app
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
