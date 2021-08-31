import React, {useState, useEffect} from "react"
import UserProfile from "./UserProfile"

function DiscordLogin({auth_params}){
    console.log('DiscordLogin')
    console.log(auth_params)
    let state = "hi"
    let code = "bye"
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [guilds, setGuilds] = useState(null);
    const [user, setUser] = useState(null)
    const [isUserLoaded, setIsUserLoaded] = useState(null)
    console.assert(state === "hi")

    const API_ENDPOINT = 'https://discord.com/api/v9'

    useEffect(() => {
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
            <div>
                <div>
                    User: {isUserLoaded?<UserProfile user={user}/>:"Loading..."}
                </div>
                <ul>
                    {guilds.map(item => (
                    <li key={item.id}>
                        {item.owner? <img
                            style={{width:"20px"}}
                            src="https://cdn.icon-icons.com/icons2/2248/PNG/512/crown_icon_135729.png"
                            alt="Owner Icon"
                        />:null} 
                        {item.name} 
                        {item.icon? <img
                            style={{width:"20px"}}
                            src={`https://cdn.discordapp.com/icons/${item.id}/${item.icon}.webp?size=128`}
                            alt="Owner Icon"
                        />:null} 
                        {item.permissions}<br/>
                        Admin:{(item.permissions&8)>0?"Yes":"No"} 
                    </li>
                    ))}
                </ul>
            </div>
        )
      }
}


export default DiscordLogin