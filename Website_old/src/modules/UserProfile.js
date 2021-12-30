import React from "react"


function UserProfile({user}){
    console.log(user)
    return (
        <div>
            {user.username}#{user.discriminator}
            <br/>
            <img
                src={`https://cdn.discordapp.com/banners/${user.id}/${user.banner}.${user.banner.substring(0,2) === "a_"?"gif":"png"}?size=128`}
                alt="profile icon"
            />
            <br/>
            <img
                src={`https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png?size=128`}
                alt="profile icon"
            />

        </div>
    )
}
//

export default UserProfile
