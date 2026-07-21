# Étage de compilation: outils de build (gcc, en-têtes libpq) nécessaires
# pour compiler les extensions C de certaines dépendances, jamais utiles à
# l'exécution - isolés ici pour ne pas alourdir l'image finale.
FROM python:3.12-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Couche dépendances séparée du code applicatif: tant que pyproject.toml ne
# change pas, ce `pip install` reste en cache même si `app/` change à chaque
# build (cas courant en itération).
COPY pyproject.toml ./
RUN pip install --no-cache-dir --prefix=/install .

# Image finale: uniquement l'environnement Python déjà construit + le code
# applicatif, sans compilateur ni en-têtes de développement.
FROM python:3.12-slim
WORKDIR /app

RUN useradd --create-home --uid 1000 --shell /usr/sbin/nologin iumc \
    && mkdir -p /data/media \
    && chown iumc:iumc /data/media

COPY --from=builder /install /usr/local
COPY --chown=iumc:iumc app ./app
COPY --chown=iumc:iumc migrations ./migrations
COPY --chown=iumc:iumc alembic.ini ./

USER iumc
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
	CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/openapi.json', timeout=2)" || exit 1

# --proxy-headers/--forwarded-allow-ips: le backend n'est jamais exposé
# directement en prod (voir infra/docker-compose.prod.yml, ports: []), seul
# Nginx l'est; on peut donc faire confiance à ses en-têtes X-Forwarded-*
# pour retrouver la vraie IP cliente (sinon request.client.host vaut
# toujours l'IP interne de Nginx, ce qui casse à la fois l'IP loggée dans
# le journal d'audit et le rate-limiting par IP des formulaires publics).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
