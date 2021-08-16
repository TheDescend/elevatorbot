FROM node:latest

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/Website/node_modules/.bin:$PATH

WORKDIR /app/Website

COPY package.json .

RUN npm install

COPY . .

CMD npm start
