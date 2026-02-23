### Stage 1: Build React app
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install --frozen-lockfile 2>/dev/null || npm install

COPY . .
RUN npm run build

### Stage 2: Serve via nginx with /api proxy to backend
FROM nginx:1.25-alpine

# Copy built SPA
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config (nginx.conf is inside the frontend build context)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
