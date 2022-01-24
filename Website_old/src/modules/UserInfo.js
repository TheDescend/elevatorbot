import React from "react"
import {useParams} from "react-router"
import UserProfile from "./UserProfile"

export default function UserInfo({userfunctions, guildfunctions}){
    const [getUser, setUser] = userfunctions
    const [getGuilds, setGuilds] = guildfunctions

    let { userid } = useParams();
    if (!getUser())
        return <h2>"Unauthenticated"</h2>
    return (
        <div>
            <div>
                User: <UserProfile user={getUser()}/>
            </div>
            <ul>
                {getGuilds().map(item => (
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
