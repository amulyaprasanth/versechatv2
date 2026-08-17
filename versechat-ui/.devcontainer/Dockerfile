FROM node:22-slim AS deps

WORKDIR /workspace

COPY package.json package-lock.json ./

RUN npm ci --no-audit --no-fund


FROM node:22-slim

WORKDIR /workspace

COPY --from=deps /workspace/node_modules ./node_modules

EXPOSE 3000

USER node

CMD ["npm", "run", "dev"]
