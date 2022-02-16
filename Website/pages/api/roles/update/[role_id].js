import {getSession} from "next-auth/react";
import {getGuilds} from "../../../../lib/discord";
import {hasDiscordPermission} from "../../../../lib/discordPermission";
import request from "../../../../lib/http";

export default async function handler(req, res) {
    const { role_id } = req.query
    const guild_id = req.body.guild_id
    const checkFailure = await checkOk(req, res)

    if (checkFailure != null) {
        res.status(500).json({
            content: checkFailure
        })
        return
    }

    // post to backend
    const data = await request(
        "POST",
        `/destiny/roles/${guild_id}/update/${role_id}`,
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


export async function checkOk(req, res) {
    const session = await getSession({req})

    // check session
    if (!session) {
        return "You are not authenticated with Discord"
    }

    // get user guilds
    const guilds = await getGuilds(session)
    if (!guilds) {
        return "Discord is having troubles, try again later"
    }
    const guild_id = req.body.guild_id
    let guild = null
    guilds.forEach(function (g) {
        if (g.id === String(guild_id)) {
            guild = g
        }
    })

    // check admin perms
    const adminPerms = hasDiscordPermission(guild)
    if (!adminPerms) {
        return "You do not have admin permissions in this server"
    }

    return null
}
