# Home Network Scanner Docker Files

Put these files in the root of your project.

## Files included
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

## Before you build
1. Make sure your project root contains:
   - `requirements.txt`
   - `app/`
   - `.env`
2. Keep your existing `.env` file in the project root.
3. If you use passkeys, access the app through `https://localhost` behind your reverse proxy.

## Build and run
From your project root:

```bash
docker compose build
docker compose up
```

Then open:

```text
http://localhost:8000
```

## If you want HTTPS for passkeys
Run your reverse proxy on the host and point it to the container on port 8000.

## Notes
- `nmap` is installed inside the container.
- Docker networking can affect scan visibility depending on host OS.
- On macOS, Docker Desktop networking behaves differently than Linux. If scan reachability looks limited, that is usually a Docker networking limitation rather than an app bug.

## Optional commands
Stop:
```bash
docker compose down
```

Rebuild after code changes:
```bash
docker compose up --build
```
