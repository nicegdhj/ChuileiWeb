# syntax=docker/dockerfile:1
ARG NPM_REGISTRY=https://registry.npmmirror.com

FROM node:18-alpine AS builder
WORKDIR /app
ARG NPM_REGISTRY
RUN npm config set registry "$NPM_REGISTRY"
COPY package.json ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

FROM nginx:1.25-alpine
COPY --from=builder /app/dist/build/h5 /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
