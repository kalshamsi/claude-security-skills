# Multi-stage build for a Node.js application
# Trivy will scan this image for OS and library vulnerabilities

FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .

FROM node:18-alpine AS runtime
WORKDIR /app
COPY --from=builder /app /app

# Security best practice: run as non-root user
USER node

EXPOSE 3000

# Note: consider adding a .dockerignore to exclude node_modules, .git, tests/
CMD ["node", "src/index.js"]
