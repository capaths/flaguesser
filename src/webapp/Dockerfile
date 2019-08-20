# pre-production
FROM python:3 as production-stage

RUN apt-get update && apt-get clean

# build frontend
FROM node:lts-alpine as build-stage

WORKDIR /app

COPY webapp/frontend/package*.json ./

RUN npm install

COPY webapp/frontend/ ./

RUN npm run build

# production
FROM production-stage

COPY webapp/requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY --from=build-stage /dist /app/dist

WORKDIR /app

COPY webapp/app ./app
COPY webapp/run.py ./

ENV ENV=prod
ENV PYTHONBUFFERED=0

ENTRYPOINT ["python"]
CMD ["run.py"]
