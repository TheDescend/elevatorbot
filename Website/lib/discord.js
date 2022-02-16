import {getSetting} from "./settings";
import {getAccessToken} from "./http";

async function discordRequest(url, authHeader = null) {
    if (!authHeader) {
        authHeader = "Bot " + getSetting("DISCORD_APPLICATION_API_KEY")
    }

    const response = await fetch(
        "https://discord.com/api/v9" + url,
        {
            method: "GET",
            headers: {
                "Authorization": authHeader
            },
        }
    )
    return {data: await response.json(), status: response.status}
}

export async function getRoles(guildId) {
    const key = `${guildId}_roles`

    let value = global.customCache.get(key)

    if (!value) {
        const {data: roles, status: status} = await discordRequest(`/guilds/${guildId}/roles`)
        value = roles

        if (status !== 200) {
            return null
        }
        global.customCache.set(key, value)
    }

    return value
}

export async function getGuilds(session) {
    const token = await getAccessToken(session)

    const key = `${session.user.id}_guilds`

    let value = global.customCache.get(key)

    if (!value) {
        for (let i = 0; i < 5; i++) {
            const {data: guilds, status: status} = await discordRequest("/users/@me/guilds", `Bearer ${token}`)
            value = guilds

            if (status === 429) {
                await new Promise(r => setTimeout(r, (1000 * guilds["retry_after"]) + 2000))
                continue
            } else if (status !== 200) {
                return null
            }

            global.customCache.set(key, value)
            break
        }
    }

    return value
}
