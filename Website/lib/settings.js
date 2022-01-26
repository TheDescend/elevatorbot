import path from 'path'
import fs from 'fs'
import toml from 'toml'
import crypto from 'crypto'

const fullPath = path.join(process.cwd(), "settings.toml")
let settings = fs.readFileSync(fullPath, 'utf8')

// parse them
settings = toml.parse(settings)

export function getSetting(key) {
    return settings[key]
}

let secret = null

export function getSecret() {
    // also set the NEXTAUTH_URL env var
    if (!("NEXTAUTH_URL" in process.env)) {
        if (process.env.NODE_ENV === "production") {
            process.env.NEXTAUTH_URL = getSetting("WEBSITE_URL")
        }
    }

    if (secret === null) {
        const secretPath = path.join(process.cwd(), "secrets.txt")

        try {
            // read the secret file
            secret = fs.readFileSync(secretPath, 'utf8')
        } catch (error) {
            // generate a secret
            secret = crypto.randomBytes(64).toString('hex')
            fs.writeFileSync(secretPath, secret)
        }
    }
    return secret
}
