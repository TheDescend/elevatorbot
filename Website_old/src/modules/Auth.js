import React from "react"
import request from "../http";


async function Auth({ code, state }) {
    // forward the user to the backend which makes the request
    // saving the client secret in React is not secure, and we really want it to be secret

    let response = await request(
        "POST",
        "/auth/bungie",
        {
            "code": code,
            "state": state
        }
    )
    let result
    if (response.errror_message === null) {
        result = `You have successfully registered with the Bungie Name ${response.bungie_name}`
    } else {
        result = `An Error Occurred: ${response.errror_message}`
    }

    return <h3> {result} </h3>
}

export default Auth
