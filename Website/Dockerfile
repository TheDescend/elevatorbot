FROM node:latest

WORKDIR /app/Website

COPY package.json .

RUN npm install

COPY . .

CMD npm start
