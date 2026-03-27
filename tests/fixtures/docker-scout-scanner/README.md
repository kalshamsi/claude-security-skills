# docker-scout-scanner test fixture

Simulated inventory management system with two containerized services containing planted container security anti-patterns for testing the `docker-scout-scanner` skill.

## Planted vulnerabilities

### Dockerfile (Web API — node:16)

#### 1. EOL base image with known CVEs (Dockerfile)
- **File:** `Dockerfile`, line 2
- **Issue:** `node:16` reached End of Life in April 2024 and has multiple known CVEs in both Node.js runtime and the underlying Debian image. Should use a current LTS version (node:20 or node:22) with a pinned digest.

#### 2. Secrets exposed via build arguments (Dockerfile)
- **File:** `Dockerfile`, lines 4-5
- **Issue:** `DB_PASSWORD` and `API_SECRET` are passed as `ARG` values and then set as `ENV`. Build args are visible in the image layer history via `docker history`. Should use BuildKit secret mounts (`--mount=type=secret`).

#### 3. Unnecessary packages installed (Dockerfile)
- **File:** `Dockerfile`, lines 11-17
- **Issue:** `vim`, `net-tools`, `telnet` are debugging tools with no production purpose. They increase attack surface and image size. Only install packages required for the application to run.

#### 4. ADD with remote URL (Dockerfile)
- **File:** `Dockerfile`, line 21
- **Issue:** `ADD` with a remote URL downloads content without checksum verification. The downloaded file could be tampered with (MITM). Should use `COPY` with a locally verified file, or `RUN curl` with checksum validation.

#### 5. Debug port exposed (Dockerfile)
- **File:** `Dockerfile`, line 27
- **Issue:** Port 9229 is the Node.js debugger port. Exposing it in production allows remote debugging and code execution. Only expose application ports.

#### 6. Shell form CMD (Dockerfile)
- **File:** `Dockerfile`, line 30
- **Issue:** `CMD node server.js` uses shell form, which runs the process as a child of `/bin/sh`. This prevents proper signal handling (SIGTERM) and makes the container harder to stop gracefully. Should use exec form: `CMD ["node", "server.js"]`.

#### 7. Running as root (Dockerfile)
- **File:** `Dockerfile` (entire file)
- **Issue:** No `USER` directive — the container runs as root by default. A compromised application has full root privileges inside the container. Should add `RUN addgroup --system app && adduser --system --ingroup app app` and `USER app`.

#### 8. No HEALTHCHECK (Dockerfile)
- **File:** `Dockerfile` (entire file)
- **Issue:** No `HEALTHCHECK` instruction. The orchestrator cannot determine if the application inside the container is actually healthy and serving requests. Should add `HEALTHCHECK CMD curl -f http://localhost:3000/health || exit 1`.

### Dockerfile.worker (Background worker — python:3.8-slim)

#### 9. EOL Python base image (Dockerfile.worker)
- **File:** `Dockerfile.worker`, line 2
- **Issue:** `python:3.8-slim` reached End of Life in October 2024. Contains known CVEs in Python runtime and system libraries. Should use python:3.12-slim or newer.

#### 10. No multi-stage build (Dockerfile.worker)
- **File:** `Dockerfile.worker` (entire file)
- **Issue:** gcc and libpq-dev are build-time dependencies installed in the final image. A multi-stage build should compile dependencies in a builder stage and copy only the compiled artifacts to a slim runtime stage.

#### 11. Unnecessary packages in worker (Dockerfile.worker)
- **File:** `Dockerfile.worker`, lines 5-10
- **Issue:** `vim` has no purpose in a production worker container. `gcc` and `libpq-dev` are build dependencies that should be in a builder stage, not the runtime image.

#### 12. Running as root (Dockerfile.worker)
- **File:** `Dockerfile.worker` (entire file)
- **Issue:** No `USER` directive. The worker process runs as root. Should create and switch to a non-root user.

#### 13. Missing COPY --chown (Dockerfile.worker)
- **File:** `Dockerfile.worker`, lines 17-18
- **Issue:** Files are copied as root. Even if a USER directive were added later, the application files would still be owned by root. Should use `COPY --chown=worker:worker . .`.

### docker-compose.yml

#### 14. Privileged container (docker-compose.yml)
- **File:** `docker-compose.yml`, line 33
- **Issue:** `privileged: true` on the worker service gives the container full access to the host's devices and kernel capabilities. This effectively disables container isolation. Almost never necessary — use specific `cap_add` entries instead.

#### 15. Host filesystem mounted (docker-compose.yml)
- **File:** `docker-compose.yml`, line 18
- **Issue:** `/etc` from the host is mounted into the API container. This exposes sensitive host configuration files (passwd, shadow, ssh keys) to the containerized application.

#### 16. Docker socket mounted (docker-compose.yml)
- **File:** `docker-compose.yml`, line 35
- **Issue:** Mounting `/var/run/docker.sock` into a container gives it full control over the Docker daemon — effectively root access to the host. Should use a Docker API proxy with restricted permissions if container management is needed.

#### 17. Database credentials in plaintext (docker-compose.yml)
- **File:** `docker-compose.yml`, lines 45-47
- **Issue:** Postgres password (`admin123`) is hardcoded in the compose file. Should use Docker secrets or environment variable references to external secret management.

#### 18. Services bound to all interfaces (docker-compose.yml)
- **File:** `docker-compose.yml`, lines 48, 53
- **Issue:** Postgres (5432) and Redis (6379) are exposed on all interfaces without binding to 127.0.0.1. These internal services should not be directly accessible from outside the Docker network. Use `127.0.0.1:5432:5432` or remove the port mapping entirely.
