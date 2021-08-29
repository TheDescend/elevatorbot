import React from "react"

function Auth({ code, state }) {
    //[discordID, serverID] = state.split(":")

    var url = 'https://www.bungie.net/platform/app/oauth/token/'
    var headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'authorization': 'Basic ' + Buffer.from("37440:rCCFPpK5jQezXen-gTJp7QqY6cZLbVBI7Rd6gkby-gQ").toString('base64'), //elevatortest credentials
        'origin': 'localhost:3000'
      }

    var data = `grant_type=authorization_code&code=${code}`


    //var time_now = Date.now();
    fetch(url, {
      method: "POST", 
      headers: headers,
      body: data
    }).then(res => {
      //TODO add error handling
      if (res.ok)
        var backend_host = process.env.BACKEND_HOST
        var backend_port = process.env.BACKEND_PORT
        var backend_url = `${backend_host}:${backend_port}/auth/bungie`
        fetch(backend_url, {
          method: "POST", 
          headers: {"hi": "Kigstn"},
          body: JSON.stringify({
            ...res,
            state: state
          })
        })
    });

  return <h3>These are not the html tags you are looking for</h3>
}

export default Auth