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
    // pages: {
    //     signIn: '/auth/signin',
    //     signOut: '/auth/signout',
    //     error: '/auth/error', // Error code passed in query string as ?error=
    //     verifyRequest: '/auth/verify-request', // (used for check email message)
    //     newUser: '/auth/new-user' // New users will be directed here on first sign in (leave the property out if not of interest)
    // },

   //  pages: {
   //      signIn: '/auth/discord',
   // },
})
