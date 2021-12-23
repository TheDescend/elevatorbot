FROM node:latest AS site_compile
RUN apt-get update && apt-get upgrade -y

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/Website/node_modules/.bin:$PATH

ENV CHOKIDAR_USEPOLLING true

# copy over the required files
COPY ./settings.py /app/settings.py
COPY ./ElevatorBot/docs /app/ElevatorBot/docs
COPY ./Website /app/Website

# instructions in package.json
WORKDIR /app/Website
RUN npm install
RUN npm run build


FROM nginx:latest
RUN apt-get update && apt-get upgrade -y

COPY --from=site_compile /app/Website/build /usr/share/nginx/html
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
#CMD ["nginx", "-g", "daemon off;"]
