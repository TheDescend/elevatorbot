export default function RoleForm({role, adminPerms}) {
    const registerUser = async event => {
        event.preventDefault()

        // https://nextjs.org/blog/forms
        const res = await fetch(`/api/${role_id}`, {
            body: JSON.stringify({
                name: event.target.name.value
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        })

        const result = await res.json()
    }

    return (
        <form onSubmit={registerUser} className="pl-2 pt-2">
            <p> discord_role_id</p>
            <input id="role_name" name="name" type="text" placeholder="name" required/>

            {
                role["role_data"].map((data) => {
                        return (
                            <div>
                                {
                                    Object.keys(data).map((key) => {
                                        return (
                                            <HandleRoleReq
                                                key={key}
                                                data={data[key]}
                                            />
                                        )
                                    })
                                }
                            </div>
                        )
                    }
                )
            }

            <button type="submit">Register</button>
        </form>
    )
}


function HandleRoleReq({key, data}) {
    let format
    let name

    if (key === "require_activity_completions") {
        format = <HandleActivities data={data}/>
        name = "Required Activities"
    } else if (key === "require_collectibles") {
        format = <HandleCollectibles data={data}/>
        name = "Required Collectibles"
    } else if (key === "require_records") {
        format = <HandleRecords data={data}/>
        name = "Required Triumphs"
    } else{
        format = <HandleRoles data={data}/>
        name = "Required Roles"
    }

    return (
        <div>
            <p>
                {name}
            </p>
            {format}
        </div>
    )
}

function HandleActivities({data}) {
    return (
        <div>

        </div>
    )
}

function HandleCollectibles({data}) {
    return (
        <div>

        </div>
    )
}

function HandleRecords({data}) {
    return (
        <div>

        </div>
    )
}

function HandleRoles({data}) {
    return (
        <div>

        </div>
    )
}
