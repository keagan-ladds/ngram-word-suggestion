FROM node:14 as node

WORKDIR /usr/src/app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/. .
RUN npm run build

FROM python:3
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
COPY --from=node /usr/src/app/frontend/dist/frontend /usr/src/app/static/.

EXPOSE 5000

CMD [ "python", "./app.py" ]