FROM node:lts-alpine

RUN npm install -g http-server

WORKDIR /app

COPY webapp/frontend/package*.json ./

RUN npm install

COPY webapp/frontend/ ./

RUN npm run build

CMD ["sh", "-c", "http-server -p ${PORT} dist"]
