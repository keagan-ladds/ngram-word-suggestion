FROM node:14

WORKDIR /usr/src/app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/. .
RUN npm run build

FROM python:3.6.8
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python app.py