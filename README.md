# Elevator Bot

> The bot is used in the <a href="https://www.bungie.net/en/ClanV2?groupid=4107840">THE DESCEND</a> Discord

> Using discord-py for the bot and flask for the webserver

- requires python 3.9+
- dependencies are in requirements.txt
- for issues, check this github

## config.py

- COMMAND_PREFIX = "!"
- NOW_PLAYING = COMMAND_PREFIX + "commands"

"The tokens. Keep them secret:"

- BOT_TOKEN = *DISCORD-BOT-TOKEN*
- BUNGIE_TOKEN = *BUNGIE-API-TOKEN*
- BUNGIE_RR_TOKEN = *BUNGIE-RR-TOKEN*
- BUNGIE_BT_TOKEN = *BUNGIE-BT-TOKEN*
- BUNGIE_OAUTH = *BUNGIE-OAUTH-TOKEN*
- BUNGIE_SECRET = *BUNGIE-OAUTH-SECRET*
- B64_SECRET = *B64-SECRET*
- STEAM_TOKEN = *STEAM-API-TOKEN*
- NEWTONS_WEBHOOK = *NEWTONS_WEBHOOK*
- CLANID = *DESTINY-CLAN-ID*
- BOTDEVCHANNELID = *DISCORD-BOT-DEV-CHANNEL-ID*
- DISCORDCLANROLEID = *DISCORD-CLAN-ROLE-ID*

## Commands available through the bot

### !addrolestoregistered

Assigns the roles @Registered or @Not Registered to everyone. This shows whether they have linked their destiny account
through the bot.

### !assignallroles

For all registered members, checks for which roles from static/dict.py each member is eligible and assigns them
accordingly.

### !boosters

Shows a list of people who used their Nitro subscription to boost the server.

### !checknames

Checks for all discord guild members whether they have a destiny-account linked and prints either the raid.report link
or 'not found'

### !checknewbies

Checks for all bungie-net clan members whether they have a discord account associated and if it's still a member of the
server

### !checkregister

Checks whether the caller has a destiny-account connected and prints it's ID

### !commands

Shows all commands that aren't tagged with a \[Tag\]

### !dr

Prints the users dungeon.report link

### !finish [start of text]

Uses a continuously updated markov chain generated from the most coherent discord channels to finish whatever sentence
you type as argument

### !flawlesses

Prints all the activityIDs for whom a completion with 0 deaths has been logged

### !forceregister discordID destinyID

Adds the discordID - destinyID pair to the database. This will usually be done through the !register command and a
signup via bungie and should only be used if necessary

### !friends

Interactive message to build a graph depending on your past teammates within Destiny 2

### !funfact

Prints a fun fact

### !getapikey

Sends you the api key used by the bot for you if requested via DMs

### !getdestinyID [discord Identifier]

Returns the destinyID if the discordid was found in the DB. Member conversion from the argument relies on discordpy's
MemberConverter.

### !getdiscordfuzzy [partial name]

Will search the given partial name in the bungie-net clan and returns a list of possible matches for both destinyID and
discordID

### !getdiscordid [destinyID]

Gets the discordID from the DB if there's a match or informs you of it's absence

### !getroles [discordUser]

Using discordpy's MemberConverter. Gets all the roles from static/dict.py a user is eligible for.

### !getsheet

Generates an Excelsheet containing the current state for registrated members on their roles

### !getusermatching

Checks for all clanmembers whether they are/were in the discord server or not

### !initiateDB

Adds all messages form the eligible channels to the markov-chat samples

### !lastraid

Some stats about the last raid activity done

### !makechannelothergameroles

Clears the channel and sets up a post that allows for reaction-based roles

### !markov

Generates a random message based on the markov-chains collected in the discord server

### !maxpower

Checks all the registered users for a ranking of the highest 20 powerlevels

### !mystic

Shows mystics list of who needs trials carries

### !mysticAdd/mysticremove

Add/Remove yourself onto/from the mystic-carry-list Admins can use this with a discordUser as parameter

### !poptimeline

Generates a graph depicting the active users since Shadowkeep

### !rasputin

Was used to track progress of the community quest during season of worthy

### !rasputingraph

Displays a graph of the progress of the community quest during season of worthy

### !register

Registers you to the bots DB, by sending you a link to the oauth-page on elevatorbot.ch

### !registerdesc

Shadows !register, but don't get picked up from Charlemange.

### !removeallroles [discord user]

Removes a users roles

### !rolerequirements [role name]

Shows what you already have towards a certain role within static/dict.py

### !rollreaction [k]

Chooses k distinct people from the reactions to the message before this one

### !rr

Prints the link to your personal raid.report

### !spoder

Prints the spiders inventory, displaying the material costs and how many you already own

### !stat [statname]

Use !stat help for a list of all possibilites. Gives various statistics about your ingame accomplishments.

### !unregister [discord user]

Removes a user from the bots DB

### !updateDB

Updates all the users in the DB with their most recent activities

## Support

Reach out to me at one of the following places!

- LinkedIn at <a href="https://www.linkedin.com/in/lukas-schmid-9b9711179/" target="_blank">`Linked Schmid`</a>
- Twitter at <a href="http://twitter.com/haligaliman" target="_blank">`@haligaliman`</a>