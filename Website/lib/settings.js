import path from 'path'
import fs from 'fs'
import toml from 'toml'
import crypto from 'crypto'

const fullPath = path.join(process.cwd(), "settings.toml")
global.settings = fs.readFileSync(fullPath, 'utf8')

// parse them
global.settings = toml.parse(settings)

export function getSetting(key) {
    return global.settings[key]
}

global.secret = null

export function getSecret() {
    // also set the NEXTAUTH_URL env var
    if (!("NEXTAUTH_URL" in process.env)) {
        if (process.env.NODE_ENV === "production") {
            process.env.NEXTAUTH_URL = getSetting("WEBSITE_URL")
        }
    }

    if (global.secret === null) {
        const secretPath = path.join(process.cwd(), "secrets.txt")

        try {
            // read the secret file
            global.secret = fs.readFileSync(secretPath, 'utf8')
        } catch (error) {
            // generate a secret
            global.secret = crypto.randomBytes(64).toString('hex')
            fs.writeFileSync(secretPath, global.secret)
        }
    }
    return global.secret
}
