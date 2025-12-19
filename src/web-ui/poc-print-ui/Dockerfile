# Stage 1: Build the app
FROM node:alpine as build

WORKDIR /app
COPY package.json package-lock.json ./

RUN npm install
RUN npm install -g @angular/cli

COPY . .

RUN ng build --configuration=production

# Stage 2: Prepare Nginx to serve static files
FROM nginx:alpine

COPY --from=build app/dist/poc-print-ui /usr/share/nginx/html