import NextAuth from 'next-auth'
import DiscordProvider from "next-auth/providers/discord";
import {getSecret, getSetting} from "../../../lib/settings";

export default NextAuth({
    providers: [
        DiscordProvider({
            clientId: getSetting("DISCORD_CLIENT_ID"),
            clientSecret: getSetting("DISCORD_CLIENT_SECRET"),
            authorization: "https://discord.com/api/oauth2/authorize?scope=guilds+identify",
        })
    ],
    secret: getSecret(),
    callbacks: {
        async jwt({token, account}) {
            if (account) {
                token.accessToken = account.access_token;
            }
            return token;
        },
        async session({session, token, user}) {
            session.accessToken = token.accessToken;
            return session;
        },
    },
})
