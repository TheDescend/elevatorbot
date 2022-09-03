1) Clone this repo
2) Put your env info (token etc) in `.env.bot` like in `.env.bot.example`
3) Launch docker compose stack via `docker-compose up -d --build`
4) Go to http://grafana.localhost:3000/
5) Go to `+` (on side panel) -> `import` -> select `grafana_dashboard.json` file from this repo, select `Prometheus` data source
6) Modify your bot in `bot/main.py` etc, re-launch via `docker-compose up -d --build`
7) Put your bot requirements to `bot/requirements.txt`

Your bot runs inside docker container, as it should've been

Grafana and Prometheus are run via docker-compose in thier own containers. They are already pre-configured

Stats scale/client/extension configured to expose http `/metrics` endpoint (internally by default) that is scraped by Prometheus
