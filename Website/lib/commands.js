import path from 'path'
import fs from 'fs'

const docsDirectory = path.join(process.cwd(), 'data/docs')

export function getCommandJson( name ) {
    // Read json file
    const fullPath = path.join(docsDirectory, name)
    const fileContents = fs.readFileSync(fullPath, 'utf8')
    return JSON.parse(fileContents)
}
