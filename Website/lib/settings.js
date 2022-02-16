import path from 'path'
import fs from 'fs'
import toml from 'toml'


export function getSetting(key) {
    if (!("setting" in global)) {
        const fullPath = path.join(process.cwd(), "settings.toml")
        global.settings = fs.readFileSync(fullPath, 'utf8')

        // parse them
        global.settings = toml.parse(settings)
    }

    return global.settings[key]
}


export function getSecret() {
    // also set the NEXTAUTH_URL env var
    if (!("NEXTAUTH_URL" in process.env)) {
        if (process.env.NODE_ENV === "production") {
            process.env.NEXTAUTH_URL = getSetting("WEBSITE_URL")
        }
    }

    return getSetting("SECRET")
}
