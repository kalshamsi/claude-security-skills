# Web application Dockerfile — inventory management API
FROM node:16

# Build arguments for configuration
ARG DB_PASSWORD=inventory_db_pass_2023
ARG API_SECRET=HARDCODED_STRIPE_KEY_DO_NOT_USE

ENV NODE_ENV=production
ENV DB_PASSWORD=${DB_PASSWORD}
ENV API_SECRET=${API_SECRET}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    curl \
    wget \
    vim \
    net-tools \
    telnet \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application files
ADD https://raw.githubusercontent.com/example/config/main/default.json /app/config/default.json
COPY package*.json ./
RUN npm ci --only=production
COPY . .

EXPOSE 3000
EXPOSE 9229

# Start the application
CMD node server.js
