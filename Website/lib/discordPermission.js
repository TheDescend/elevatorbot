export function hasDiscordPermission(guild) {
    if (guild["owner"] === true) {
        return true
    }
    const perms = guild["permissions"]
    const adminPerms = 1 << 3

    return !!(adminPerms & perms)
}
