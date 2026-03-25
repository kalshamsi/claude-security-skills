# Deliberately insecure Dockerfile — used as a test fixture for docker-scout-scanner
# DO NOT use in production. Every issue here is intentional.

# Issue 1: Using 'latest' tag — CWE-1104, A06
# Issue 8: Non-official base image (would be caught if registry prefix were added)
FROM ubuntu:latest

# Issue 3: Hardcoded secret in build arg — CWE-798, A07
ARG DB_PASSWORD=hunter2
ARG API_TOKEN=sk-live-abcdef123456

# Issue 4: apt-get install without --no-install-recommends — CWE-250, A01
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    build-essential \
    gcc \
    make \
    nodejs \
    npm \
    python3 \
    git

WORKDIR /app

# Issue 7: ADD instead of COPY for local files — CWE-829, A08
ADD . /app/

# Issue 7 (remote URL variant): ADD fetching a remote archive — CWE-829, A08
# ADD https://example.com/vendor.tar.gz /app/vendor/

# Bake the build arg secret into a layer — makes it retrievable via docker history
RUN echo "DB_PASSWORD=$DB_PASSWORD" >> /app/.env && \
    echo "API_TOKEN=$API_TOKEN" >> /app/.env

RUN npm install
RUN npm run build

# Issue 9: No USER directive — container runs as root — CWE-250, A01
# (USER instruction is intentionally omitted)

# Issue 9 (exposed ports): Exposes port 22 (SSH) unnecessarily — CWE-284, A01
EXPOSE 22
EXPOSE 80
EXPOSE 3000
EXPOSE 5432

# Issue 5: No HEALTHCHECK directive — CWE-693, A07
# (HEALTHCHECK intentionally omitted)

# Issue 6: No multi-stage build — build tools (gcc, make, npm) are present in
#           the final image, inflating the attack surface — CWE-1104, A06

# Issue 10: Shell form CMD instead of exec form — CWE-693, A07
#           /bin/sh -c wraps the process; SIGTERM not forwarded to node
CMD node /app/server.js
