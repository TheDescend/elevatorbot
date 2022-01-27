import path from 'path'
import fs from 'fs'
import toml from 'toml'
import crypto from 'crypto'


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

    const key = `secret`

    let value = global.customCache.get(key)

    if (!value) {
        const secretPath = path.join(process.cwd(), "secrets.txt")

        try {
            // read the secret file
            value = fs.readFileSync(secretPath, 'utf8')
        } catch (error) {
            // generate a secret
            value = crypto.randomBytes(64).toString('hex')
            fs.writeFileSync(secretPath, value)
        }
        global.customCache.set(key, value, 0)
    }
    return value
}
