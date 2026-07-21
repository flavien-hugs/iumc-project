# Contexte de build attendu : la racine du monorepo frontend (frontend/).
#
# Étage "deps" isolé de la couche source : tant que les package.json (ce
# monorepo npm workspaces en a 5 : racine + 2 apps + 2 packages) ne changent
# pas, `npm ci` reste en cache même si le code source change à chaque build -
# ce qui est le cas courant en itération. Cet étage est identique dans le
# Dockerfile de apps/admin : construit dans le même contexte, il est réutilisé
# tel quel par le cache de build au lieu d'être refait deux fois.
FROM node:22-alpine AS deps
WORKDIR /repo
COPY package.json package-lock.json ./
COPY apps/website/package.json apps/website/
COPY packages/ui/package.json packages/ui/
COPY packages/api/package.json packages/api/
RUN npm ci

FROM deps AS build
COPY . .
RUN npm run build --workspace=@iumc/website

# Image finale : uniquement le résultat du build (adapter-node produit un
# bundle autonome, aucun node_modules n'est nécessaire à l'exécution) -
# le package.json reste requis, Node s'en sert pour savoir que le bundle
# ESM émis par adapter-node doit être interprété en mode module.
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build --chown=node:node /repo/apps/website/build ./build
COPY --from=build --chown=node:node /repo/apps/website/package.json ./

USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
	CMD node -e "fetch('http://localhost:3000/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

CMD ["node", "build"]
