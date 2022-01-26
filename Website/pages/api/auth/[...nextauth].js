import NextAuth from 'next-auth'
import DiscordProvider from "next-auth/providers/discord";
import {getSetting, getSecret} from "../../../lib/settings";

export default NextAuth({
    providers: [
        DiscordProvider({
            clientId: getSetting("DISCORD_CLIENT_ID"),
            clientSecret: getSetting("DISCORD_CLIENT_SECRET"),
            authorization: "https://discord.com/api/oauth2/authorize?scope=guilds+guilds.members.read+identify",
        })
    ],
    secret: getSecret(),
})
