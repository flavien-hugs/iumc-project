# Contexte de build attendu : la racine du monorepo frontend (frontend/).
#
# Étage "deps" identique à celui de apps/website/Dockerfile (mêmes fichiers
# copiés, même commande) : le cache de build Docker le partage entre les deux
# images tant que les package.json n'ont pas changé, même en construisant
# l'un puis l'autre séparément.
FROM node:22-alpine AS deps
WORKDIR /repo
COPY package.json package-lock.json ./
COPY apps/admin/package.json apps/admin/
COPY packages/ui/package.json packages/ui/
COPY packages/api/package.json packages/api/
RUN npm ci

FROM deps AS build
COPY . .
RUN npm run build --workspace=@iumc/admin

# Image finale : uniquement le résultat du build (adapter-node produit un
# bundle autonome, aucun node_modules n'est nécessaire à l'exécution) -
# le package.json reste requis, Node s'en sert pour savoir que le bundle
# ESM émis par adapter-node doit être interprété en mode module.
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build --chown=node:node /repo/apps/admin/build ./build
COPY --from=build --chown=node:node /repo/apps/admin/package.json ./

USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
	CMD node -e "fetch('http://localhost:3000/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

CMD ["node", "build"]
