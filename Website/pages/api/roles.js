import {getSession} from "next-auth/react";
import {getGuilds} from "../../lib/discord";
import {hasDiscordPermission} from "../../lib/discordPermission";
import request from "../../lib/http";

export default async function handler(req, res) {
    const session = await getSession({req})

    // check session
    if (!session) {
        res.status(500).json({
            content: "You are not authenticated with Discord"
        })
        return
    }

    // get user guilds
    const guilds = await getGuilds(session)
    if (!guilds) {
        res.status(500).json({
            content: "Discord is having troubles, try again later"
        })
        return
    }
    const guild_id = req.body.guild_id
    let guild = null
    guilds.forEach(function (g) {
        if (g.id === String(guild_id)) {
            guild = g
        }
    })

    // todo test
    // check admin perms
    const adminPerms = hasDiscordPermission(guild)
    if (!adminPerms) {
        res.status(500).json({
            content: "You do not have admin permissions in this server"
        })
        return
    }

    // post to backend
    const data = await request(
        "POST",
        `/destiny/roles/${guild_id}/upsert`,
        req.body,
    )

    if (data.status_code === 200) {
        res.status(200).json({
            content: "Role has been updated!"
        })
    } else {
        res.status(500).json({
            content: data.content
        })
    }
}
