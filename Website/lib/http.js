export default async function request(method, path, body=null ) {
    const backend_host = process.env.BACKEND_HOST
    const backend_port = process.env.BACKEND_PORT
    const url = `http://${backend_host}:${backend_port}${path}`
    const headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }

    let response
    if (body) {
        response = await fetch(
            url,
            {
                method: method,
                headers: headers,
                body: JSON.stringify(body),
            }
        )
    } else {
        response = await fetch(
            url,
            {
                method: method,
                headers: headers,
            }
        )
    }

    const result = await response.json()
    if (response.status === 409) {
        return {
            "status_code": response.status,
            "content": result.error
        }
    } else if (response.ok) {
        return {
            "status_code": response.status,
            "content": result
        }
    } else {
        return {
            "status_code": response.status,
            "content": JSON.stringify(result.detail[0])
        }
    }
}
