import {getSetting} from "./settings";

async function discordRequest(url) {
    const response = await fetch(
        "https://discord.com/api/v9" + url,
        {
            method: "GET",
            headers: {
                "Authorization": "Bot " + getSetting("DISCORD_APPLICATION_API_KEY")
            },
        }
    )
    return {data: await response.json(), status: response.status}
}

export async function getRoles(guildId) {
    const key = `${guildId}_roles`

    let value = global.customCache.get(key)

    if (!value){
        const {data: roles, status: status} = await discordRequest(`/guilds/${guildId}/roles`)
        value = roles

        if (status !== 200) {
            return null
        }
        global.customCache.set(key, value)
    }

    return value
}
