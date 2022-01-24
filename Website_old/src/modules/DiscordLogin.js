import React, {useEffect, useState} from "react"
import {Redirect} from "react-router"

function DiscordLogin({auth_params, userfunctions, guildfunctions}){
    console.log('DiscordLogin')
    console.log(auth_params)
    let state = "hi"
    let code = "bye"
    const [error, setError] = useState(null)
    const [isLoaded, setIsLoaded] = useState(false)

    const [getUser, setUser] = userfunctions
    const [getGuilds, setGuilds] = guildfunctions

    const [isUserLoaded, setIsUserLoaded] = useState(null)

    console.assert(state === "hi")

    const API_ENDPOINT = 'https://discord.com/api/v9'

    useEffect(() => {
        console.log("auth params changed")
        console.log(auth_params)
        if (!auth_params)
            return
        let {access_token, expires_in, scope, state, token_type,} = auth_params
        let auth_header = token_type + " " + access_token
        fetch(`${API_ENDPOINT}/users/@me/guilds`, {
            method: 'GET',
            headers: {
                'Authorization': auth_header
            }
        }).then(data => data.json())
            .then(resp => {
                if (Array.isArray(resp)){
                    setGuilds(resp)
                    setIsLoaded(true)
                    setError(null)
                }else{
                    console.log(resp)
                    setError(`Getting guild list failed, got ${typeof(resp)} instead`)
                }

            })
    }, [auth_params])

    useEffect(() => {
        console.log("auth params changed")
        console.log(auth_params)
        if (!auth_params)
            return
        let {access_token, expires_in, scope, state, token_type,} = auth_params
        let auth_header = token_type + " " + access_token
        fetch(`${API_ENDPOINT}/users/@me`, {
            method: 'GET',
            headers: {
                'Authorization': auth_header
            }
        }).then(data => data.json())
            .then(resp => {
                if (!resp['error']){
                    setUser(resp)
                    setIsUserLoaded(true)
                    setError(null)
                    console.log(resp)
                }else{
                    console.log(resp)
                    setError(`Getting user failed, got ${typeof(resp)} instead`)
                }

            })
    }, [auth_params])

    if (error) {
        return <div>Error: {error}</div>;
      } else if (!isLoaded) {
        return <div>Loading...</div>;
      } else {
        //https://discordapi.com/permissions.html

        return (
            <Redirect to={"/userinfo/" + getUser().id} />
        )
      }
}


export default DiscordLogin
