FROM node:22-alpine AS base
WORKDIR /frontend
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Local dev
FROM base AS dev
COPY . .
CMD ["npx", "ng", "serve", "--host", "0.0.0.0", "--port", "8001", "--poll", "1000"]
