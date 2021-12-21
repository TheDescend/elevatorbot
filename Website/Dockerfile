FROM node:latest AS site_compile
RUN apt-get update && apt-get upgrade -y

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/Website/node_modules/.bin:$PATH

ENV CHOKIDAR_USEPOLLING true

WORKDIR /app/Website

COPY package.json .
COPY src src
COPY public public

# instructions in package.json
RUN npm install
RUN npm run build

FROM nginx:latest
RUN apt-get update && apt-get upgrade -y
#WORKDIR /app/Website
COPY --from=site_compile /app/Website/build /usr/share/nginx/html
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
#CMD ["nginx", "-g", "daemon off;"]