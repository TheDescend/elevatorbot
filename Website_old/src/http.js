export default async function request(method, path, body=null ) {
    let response

    const backend_host = process.env.BACKEND_HOST
    const backend_port = process.env.BACKEND_PORT
    const url = `${backend_host}:${backend_port}${path}`

    if (body) {
        response = await fetch(
            url,
            {
                method: method,
                body: JSON.stringify(body)
            }
        )
    } else {
        response = await fetch(
            url,
            {
                method: method
            }
        )
    }
    const result = await response.json()
    if (response.ok || response.status === 409 ) {
        return result
    } else {
        return {"errror_message": result}
    }
}
