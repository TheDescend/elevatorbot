[![Release](https://img.shields.io/github/v/release/TheDescend/elevatorbot?label=Version&logo=github)](https://github.com/TheDescend/elevatorbot/releases)
![Python](https://img.shields.io/badge/Python-3.10+-1081c1?logo=python)
[![Black Formatted](https://img.shields.io/github/workflow/status/TheDescend/elevatorbot/Black%20Formating/master?label=Black%20Formatting&logo=github)](https://github.com/TheDescend/elevatorbot/actions/workflows/Backend_pytest.yml)
[![Backend Test](https://img.shields.io/github/workflow/status/TheDescend/elevatorbot/Test%20Backend/master?label=Backend%20Tests&logo=github)](https://github.com/TheDescend/elevatorbot/actions/workflows/Backend_pytest.yml)
[![Pre-Commit](https://results.pre-commit.ci/badge/github/TheDescend/elevatorbot/master.svg)](https://results.pre-commit.ci/latest/github/TheDescend/elevatorbot/master)
[![Discord](https://img.shields.io/discord/669293365900214293?color=%235865F2&label=Descend%20Discord&logo=discord&logoColor=%235865F2)](https://discord.gg/descend)
[![Website](https://img.shields.io/badge/Website-elevatorbot.ch-0f80c0?logo=react)](https://elevatorbot.ch/)

<p align="center">
    <img src="https://raw.githubusercontent.com/TheDescend/elevatorbot/master/logo.png" alt="ElevatorBot Logo">
</p>


<h1 align="center">
    <hr>
    ElevatorBot
</h1>

---
<div align="center">
    <a href="https://www.urbandictionary.com/define.php?term=soon%20%28tm%29">Invite to Discord</a> | <a href="https://elevatorbot.ch/">Visit the Website</a> | <a href="https://elevatorbot.ch/docs/commands">View the Documentation</a>
</div>

---

`@ElevatorBot#7635` is a modern and open source discord bot that can be used to interact with the Destiny 2 API. He was originally created at the start of 2018 because of a desire to access information not provided by the existing Destiny 2 bot, Charlemange. He has **greatly** expanded in scope since then.

ElevatorBot is mostly written in Python using [Dis-Snek](https://github.com/Discord-Snake-Pit/Dis-Snek), [FastApi](https://github.com/tiangolo/fastapi/) and [PostgreSQL](https://github.com/postgres/postgres). The website is written in JavaScript using [Next.js](https://github.com/vercel/next.js/) and [tailwindcss](https://github.com/tailwindlabs/tailwindcss). He has explicit support for modern discord features such as slash commands, components, context menus and modals.


## Features
-[x] Clan Management (Invite / Kick)
-[x] LFG System with calendar integration
-[x] LFG supportive features like a context menu to receive bungie names
-[x] Deeply customisable achievement roles
-[x] Over **30** Destiny 2 commands ranging from stats for all weapons and activities to clan rankings
-[x] Much, much more...


## Contributing
Contributors are always welcome!
If you have any question and don't know where to start, don't hesitate to contact us on [GitHub](https://github.com/Kigstn) or discord (Kigstn#9278).


## Self-Hosting Guide
Everyone can host this bot for themselves. To set him up, follow this quick installation guide.

Note: It is recommended to simply invite the official discord bot.

1) Download and extract the [latest release](https://github.com/TheDescend/elevatorbot/releases)
2) Install `docker`
3) Install `docker-compose`
4) Rename `rename_to_settings.toml` to `settings.toml`
5) Fill out `settings.toml`
6) Run `docker-compose up --build`

*Optional:*
ElevatorBot sometimes uses discord emojis.
Since you are not in the server where the emojis are from, these will display as IDs for you.
If you want to change that, you need to change the IDs in `/ElevatorBot/static/emojis.py`.

## Security

Make sure to change the default passwords in `settings.toml`.
If you decide to add ports to the `docker-compose.yml` be aware that docker will try to publish them externally, whether your firewall allows it or not.