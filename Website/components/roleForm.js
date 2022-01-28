import GlowingButton from "./styling/glowingButton";

export default function RoleForm({role, adminPerms}) {
    const registerRole = async event => {
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

    // todo
    const discordRole = "asd"
    const replacementDiscordRole = role["role_data"]["replaced_by_role_id"]

    const divFormatting = ""
    const pFormatting = ""
    const labelFormatting = "px-1"

    const _InputFormatting = "dark:bg-gray-900 rounded-lg border-none text-descend"
    const textInputFormatting = `${_InputFormatting} focus:ring-2 focus:ring-descend invalid:text-red-700 required:ring-2 required:ring-red-700 valid:ring-0 mt-1`
    const checkboxInputFormatting = `${_InputFormatting} checked:ring-2 ring-descend`

    const _InputDivFormatting = "dark:bg-slate-700 flex border-1 p-1 rounded-lg border-white"
    const textInputDivFormatting = `${_InputDivFormatting} flex-col justify-between`
    const checkboxInputDivFormatting = `${_InputDivFormatting} flex-row justify-between items-center`


    return (
        <form onSubmit={registerRole} className="p-2">
            <div className="flex flex-col gap-4 divide-y divide-descend">
                <div className="grid grid-cols-2 gap-4">
                    <div className={`${textInputDivFormatting} `}>
                        <label className={labelFormatting} htmlFor="role_name">
                            Role Name
                        </label>
                        <input
                            className={`${textInputFormatting} `} id="role_name" name="role_name" type="text"
                            placeholder="required" required disabled={!adminPerms} defaultValue={role["role_name"]}
                        />
                    </div>
                    <div className={textInputDivFormatting}>
                        <label className={labelFormatting} htmlFor="category">
                            Role Category
                        </label>
                        <input
                            className={textInputFormatting} id="category" name="category" type="text"
                            placeholder="optional" disabled={!adminPerms} defaultValue={role["role_data"]["category"]}
                        />
                    </div>
                    <div className={textInputDivFormatting}>
                        <label className={labelFormatting} htmlFor="discord_role_name">
                            Linked Discord Role
                        </label>
                        <input
                            className={textInputFormatting} id="discord_role_name" name="discord_role_name" type="text"
                            placeholder="required" required disabled={!adminPerms} defaultValue={discordRole}
                        />
                    </div>
                    <div className={textInputDivFormatting}>
                        <label className={labelFormatting} htmlFor="replaced_by_role_id">
                            Replacement Discord Role
                        </label>
                        <input
                            className={textInputFormatting} id="replaced_by_role_id" name="replaced_by_role_id"
                            type="text"
                            placeholder="optional" disabled={!adminPerms} defaultValue={replacementDiscordRole}
                        />
                    </div>
                    <div className={checkboxInputDivFormatting}>
                        <label className={labelFormatting} htmlFor="deprecated">
                            Are any requirements sunset?
                        </label>
                        <input
                            className={`${checkboxInputFormatting}`} id="deprecated" name="deprecated" type="checkbox"
                            defaultChecked={role["role_data"]["deprecated"]} disabled={!adminPerms}
                        />
                    </div>
                    <div className={checkboxInputDivFormatting}>
                        <label className={labelFormatting} htmlFor="acquirable">
                            Allow users to earn this role
                        </label>
                        <input
                            className={checkboxInputFormatting} id="acquirable" name="acquirable" type="checkbox"
                            defaultChecked={role["role_data"]["acquirable"]} disabled={!adminPerms}
                        />
                    </div>
                </div>

                <div>
                    <div className={divFormatting}>
                        <p className={pFormatting}>
                            Required Activities
                        </p>
                        <HandleActivities data={role["role_data"]["require_activity_completions"]}/>
                    </div>
                    <div className={divFormatting}>
                        <p className={pFormatting}>
                            Required Collectibles
                        </p>
                        <HandleCollectibles data={role["role_data"]["require_collectibles"]}/>
                    </div>
                    <div className={divFormatting}>
                        <p className={pFormatting}>
                            Required Triumphs
                        </p>
                        <HandleRecords data={role["role_data"]["require_records"]}/>
                    </div>
                    <div className={divFormatting}>
                        <p className={pFormatting}>
                            Required Roles
                        </p>
                        <HandleRoles data={role["role_data"]["require_role_ids"]}/>
                    </div>
                </div>

                {adminPerms &&
                    <div className="flex justify-center p-2">
                    <GlowingButton>
                        <button className="p-1 font-bold" type="submit">Update</button>
                    </GlowingButton>
                </div>
                }
            </div>
        </form>
    )
}


function HandleActivities(
    {
        data
    }
) {
    return (
        <div>

        </div>
    )
}

function HandleCollectibles(
    {
        data
    }
) {
    return (
        <div>

        </div>
    )
}

function HandleRecords(
    {
        data
    }
) {
    return (
        <div>

        </div>
    )
}

function HandleRoles(
    {
        data
    }
) {
    return (
        <div>

        </div>
    )
}
