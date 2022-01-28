import GlowingButton from "./styling/glowingButton";
import ContentContainer from "./styling/container";
import {useState} from "react";
import {FiPlusCircle} from "react-icons/fi";


const divFormatting = "marker:text-descend"
const summaryFormatting = ""
const labelFormatting = "px-1"

const _InputFormatting = "dark:bg-gray-900 rounded-lg border-none text-descend placeholder:italic"
const textInputFormatting = `${_InputFormatting} focus:ring-2 focus:ring-descend invalid:text-red-700 required:ring-2 required:ring-red-700 valid:ring-0 mt-1`
const checkboxInputFormatting = `${_InputFormatting} checked:ring-2 ring-descend`

const _InputDivFormatting = "dark:bg-slate-700 flex border-1 p-1 rounded-lg border-white"
const textInputDivFormatting = `${_InputDivFormatting} flex-col justify-between`
const checkboxInputDivFormatting = `${_InputDivFormatting} flex-row justify-between items-center`


export default function RoleForm({role, adminPerms}) {
    const registerRole = async event => {
        console.log("getting executed...")
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

    // todo delete
    // todo edit
    // todo create

    const [activities, updateActivities] = useState(role["role_data"]["require_activity_completions"])
    const [collectibles, updateCollectibles] = useState(role["role_data"]["require_collectibles"])
    const [records, updateRecords] = useState(role["role_data"]["require_records"])
    const [reqRoles, updateReqRoles] = useState(role["role_data"]["require_role_ids"])

    function handleUpdate(key) {
        let data

        switch (key) {
            case "require_activity_completions":
                data = {
                    "allowed_activity_hashes": [],
                    "count": 1,
                    "allow_checkpoints": false,
                    "require_team_flawless": false,
                    "require_individual_flawless": false,
                    "require_score": null,
                    "require_kills": null,
                    "require_kills_per_minute": null,
                    "require_kda": null,
                    "require_kd": null,
                    "maximum_allowed_players": 6,
                    "allow_time_periods": [],
                    "disallow_time_periods": [],
                    "inverse": false,
                }
                updateActivities([...activities, data])
                return

            // the others all use the same format
            default:
                data = {
                    "id": null,
                    "inverse": false,
                }

                switch (key) {
                    case "require_collectibles":
                        updateCollectibles([...collectibles, data])
                        return

                    case "require_records":
                        updateRecords([...records, data])
                        return

                    default:
                        updateReqRoles([...reqRoles, data])
                        return
                }
        }
    }

    return (
        <form onSubmit={registerRole} className="p-2">
            <div className="flex flex-col gap-4 divide-y divide-descend">
                <div className="grid grid-cols-2 gap-4">
                    <div className={textInputDivFormatting}>
                        <label className={labelFormatting} htmlFor="role_name">
                            Role Name
                        </label>
                        <input
                            className={textInputFormatting} id="role_name" name="role_name" type="text"
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
                            Are any requirements sunset
                        </label>
                        <input
                            className={checkboxInputFormatting} id="deprecated" name="deprecated" type="checkbox"
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

                <div className="flex flex-col gap-2 pt-4">
                    <ContentContainer otherStyle={true}>
                        <details className={divFormatting}>
                            <summary className={summaryFormatting}>
                                Required Activities
                            </summary>
                            <div className="grid grid-flow-row gap-2 pl-2 pt-2">
                                <HandleActivities data={activities} adminPerms={adminPerms}/>
                                {adminPerms &&
                                    <div className="flex">
                                        <button
                                            type="button"
                                            onClick={() => {
                                                handleUpdate("require_activity_completions")
                                            }}
                                        >
                                            <FiPlusCircle className="object-contain hover:text-descend w-6 h-6"/>
                                        </button>
                                    </div>
                                }
                            </div>
                        </details>
                    </ContentContainer>
                    <ContentContainer otherStyle={true}>
                        <details className={divFormatting}>
                            <summary className={summaryFormatting}>
                                Required Collectibles
                            </summary>
                            <div className="grid grid-flow-row gap-2 pl-2 pt-2">
                                <HandleCollectibles data={collectibles} adminPerms={adminPerms}/>
                                {adminPerms &&
                                    <div className="flex">
                                        <button
                                            className=""
                                            type="button"
                                            onClick={() => {
                                                handleUpdate("require_collectibles")
                                            }}
                                        >
                                            <FiPlusCircle className="object-contain hover:text-descend w-6 h-6"/>
                                        </button>
                                    </div>
                                }
                            </div>
                        </details>
                    </ContentContainer>
                    <ContentContainer otherStyle={true}>
                        <details className={divFormatting}>
                            <summary className={summaryFormatting}>
                                Required Triumphs
                            </summary>
                            <div className="grid grid-flow-row gap-2 pl-2 pt-2">
                                <HandleRecords data={records} adminPerms={adminPerms}/>
                                {adminPerms &&
                                    <div className="flex">
                                        <button
                                            className=""
                                            type="button "
                                            onClick={() => {
                                                handleUpdate("require_records")
                                            }}
                                        >
                                            <FiPlusCircle className="object-contain hover:text-descend w-6 h-6"/>
                                        </button>
                                    </div>
                                }
                            </div>
                        </details>
                    </ContentContainer>
                    <ContentContainer otherStyle={true}>
                        <details className={divFormatting}>
                            <summary className={summaryFormatting}>
                                Required Roles
                            </summary>
                            <div className="grid grid-flow-row gap-2 pl-2 pt-2">
                                <HandleRoles data={reqRoles} adminPerms={adminPerms}/>
                                {adminPerms &&
                                    <div className="flex">
                                        <button
                                            className=""
                                            type="button "
                                            onClick={() => {
                                                handleUpdate("require_role_ids")
                                            }}
                                        >
                                            <FiPlusCircle className="object-contain hover:text-descend w-6 h-6"/>
                                        </button>
                                    </div>
                                }
                            </div>
                        </details>
                    </ContentContainer>
                </div>

                {adminPerms &&
                    <div className="flex justify-around p-2">
                        <GlowingButton glow={"opacity-20"}>
                            <button className="p-1 font-bold" type="submit">Update</button>
                        </GlowingButton>
                        <GlowingButton glow={"opacity-20"}>
                            <button className="p-1 font-bold" type="button">Delete</button>
                        </GlowingButton>
                    </div>
                }
            </div>
        </form>
    )
}


// todo need to be able to delete parts of those
function FormatRequirement({children, name}) {
    return (
        <ContentContainer otherStyle={false}>
            <details className={divFormatting}>
                <summary>
                    {name}
                </summary>
                <div className="grid grid-flow-row gap-2 pl-2 pt-2">
                    {children}
                </div>
            </details>

        </ContentContainer>
    )
}


function HandleActivities({data, adminPerms}) {
    return (
        <div className="grid grid-flow-row gap-2">
            {
                data.map((activity, index) => {
                    return (
                        <FormatRequirement name={`#${index + 1}`}>
                            <div className="grid grid-cols-2 gap-4">
                                <div className={`${textInputDivFormatting} `}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-allowed_activity_hashes`}>
                                        Allowed Activities
                                    </label>
                                    <input
                                        className={textInputFormatting}
                                        id={`require_activity_completions-${index}-allowed_activity_hashes`}
                                        name={`require_activity_completions-${index}-allowed_activity_hashes`}
                                        type="text"
                                        placeholder="required"
                                        required
                                        disabled={!adminPerms}
                                        defaultValue={activity["allowed_activity_hashes"]}
                                    />
                                </div>
                                <div className={`${textInputDivFormatting} `}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-count`}>
                                        Require Count
                                    </label>
                                    <input
                                        className={textInputFormatting}
                                        id={`require_activity_completions-${index}-count`}
                                        name={`require_activity_completions-${index}-count`}
                                        type="number"
                                        placeholder="required"
                                        required
                                        disabled={!adminPerms}
                                        defaultValue={activity["count"]}
                                    />
                                </div>
                                <div className={textInputDivFormatting}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-require_score`}>
                                        Require Score
                                    </label>
                                    <input
                                        className={textInputFormatting}
                                        id={`require_activity_completions-${index}-require_score`}
                                        name={`require_activity_completions-${index}-require_score`}
                                        type="number"
                                        placeholder="optional"
                                        disabled={!adminPerms}
                                        defaultValue={activity["require_score"]}
                                    />
                                </div>
                                <div className={textInputDivFormatting}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-require_kills`}>
                                        Require Kills
                                    </label>
                                    <input
                                        className={textInputFormatting}
                                        id={`require_activity_completions-${index}-require_kills`}
                                        name={`require_activity_completions-${index}-require_kills`}
                                        type="number"
                                        placeholder="optional"
                                        disabled={!adminPerms}
                                        defaultValue={activity["require_kills"]}
                                    />
                                </div>
                                <div className={textInputDivFormatting}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-require_kills_per_minute`}>
                                        Require Kills/min
                                    </label>
                                    <input
                                        className={textInputFormatting}
                                        id={`require_activity_completions-${index}-require_kills_per_minute`}
                                        name={`require_activity_completions-${index}-require_kills_per_minute`}
                                        type="number"
                                        placeholder="optional"
                                        disabled={!adminPerms}
                                        step="0.01"
                                        defaultValue={activity["require_kills_per_minute"]}
                                    />
                                </div>
                                <div className={textInputDivFormatting}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-require_kda`}>
                                        Require K/D/A
                                    </label>
                                    <input
                                        className={textInputFormatting}
                                        id={`require_activity_completions-${index}-require_kda`}
                                        name={`require_activity_completions-${index}-require_kda`}
                                        type="number"
                                        placeholder="optional"
                                        disabled={!adminPerms}
                                        step="0.01"
                                        defaultValue={activity["require_kda"]}
                                    />
                                </div>
                                <div className={textInputDivFormatting}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-require_kd`}>
                                        Required K/D
                                    </label>
                                    <input
                                        className={textInputFormatting}
                                        id={`require_activity_completions-${index}-require_kd`}
                                        name={`require_activity_completions-${index}-require_kd`}
                                        type="number"
                                        placeholder="optional"
                                        disabled={!adminPerms} step="0.01"
                                        defaultValue={activity["require_kd"]}
                                    />
                                </div>
                                <div className={textInputDivFormatting}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-maximum_allowed_players`}>
                                        Maximum Allowed Players
                                    </label>
                                    <input
                                        className={textInputFormatting}
                                        id={`require_activity_completions-${index}-maximum_allowed_players`}
                                        name={`require_activity_completions-${index}-maximum_allowed_players`}
                                        type="number"
                                        placeholder="optional"
                                        disabled={!adminPerms}
                                        defaultValue={activity["maximum_allowed_players"]}
                                    />
                                </div>
                                <div className={textInputDivFormatting}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-allow_time_periods`}>
                                        Allow only these time periods
                                    </label>
                                    <input
                                        className={textInputFormatting}
                                        id={`require_activity_completions-${index}-allow_time_periods`}
                                        name={`require_activity_completions-${index}-allow_time_periods`}
                                        type="text"
                                        placeholder="optional" disabled={!adminPerms}
                                        defaultValue={activity["allow_time_periods"]}
                                    />
                                </div>
                                <div className={textInputDivFormatting}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-disallow_time_periods`}>
                                        Disallow these time periods
                                    </label>
                                    <input
                                        className={textInputFormatting}
                                        id={`require_activity_completions-${index}-disallow_time_periods`}
                                        name={`require_activity_completions-${index}-disallow_time_periods`}
                                        type="text"
                                        placeholder="optional"
                                        disabled={!adminPerms}
                                        defaultValue={activity["disallow_time_periods"]}
                                    />
                                </div>
                                <div className={checkboxInputDivFormatting}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-allow_checkpoints`}>
                                        Allow checkpoint runs
                                    </label>
                                    <input
                                        className={checkboxInputFormatting}
                                        id={`require_activity_completions-${index}-allow_checkpoints`}
                                        name={`require_activity_completions-${index}-allow_checkpoints`}
                                        type="checkbox"
                                        defaultChecked={activity["allow_checkpoints"]}
                                        disabled={!adminPerms}
                                    />
                                </div>
                                <div className={checkboxInputDivFormatting}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-require_team_flawless`}>
                                        Require team flawless
                                    </label>
                                    <input
                                        className={checkboxInputFormatting}
                                        id={`require_activity_completions-${index}-require_team_flawless`}
                                        name={`require_activity_completions-${index}-require_team_flawless`}
                                        type="checkbox"
                                        defaultChecked={activity["require_team_flawless"]} disabled={!adminPerms}
                                    />
                                </div>
                                <div className={checkboxInputDivFormatting}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-require_individual_flawless`}>
                                        Require individual flawless
                                    </label>
                                    <input
                                        className={checkboxInputFormatting}
                                        id={`require_activity_completions-${index}-require_individual_flawless`}
                                        name={`require_activity_completions-${index}-require_individual_flawless`}
                                        type="checkbox"
                                        defaultChecked={activity["require_individual_flawless"]}
                                        disabled={!adminPerms}
                                    />
                                </div>
                                <div className={checkboxInputDivFormatting}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-inverse`}>
                                        Invert all settings
                                    </label>
                                    <input
                                        className={checkboxInputFormatting}
                                        id={`require_activity_completions-${index}-"inverse`}
                                        name={`require_activity_completions-${index}-inverse`}
                                        type="checkbox"
                                        defaultChecked={activity["inverse"]}
                                        disabled={!adminPerms}
                                    />
                                </div>
                            </div>
                        </FormatRequirement>
                    )
                })
            }
        </div>
    )
}


function HandleCollectibles({data, adminPerms}) {
    return (
        <div className="grid grid-flow-row gap-2">
            {
                data.map((collectible, index) => {
                    return (
                        <FormatRequirement name={`#${index + 1}`}>
                            <div className="grid grid-cols-1 gap-4">
                                <div className={`${textInputDivFormatting} `}>
                                    <label className={labelFormatting} htmlFor={`require_collectibles-${index}-id`}>
                                        Require Collectible
                                    </label>
                                    <input
                                        className={textInputFormatting}
                                        id={`require_collectibles-${index}-id`}
                                        name={`require_collectibles-${index}-id`}
                                        type="text"
                                        placeholder="required"
                                        required
                                        disabled={!adminPerms}
                                        defaultValue={collectible["id"]}
                                    />
                                </div>
                                <div className={checkboxInputDivFormatting}>
                                    <label className={labelFormatting} htmlFor={`require_collectibles-${index}-inverse`}>
                                        Invert all settings
                                    </label>
                                    <input
                                        className={checkboxInputFormatting}
                                        id={`require_collectibles-${index}-"inverse`}
                                        name={`require_collectibles-${index}-inverse`}
                                        type="checkbox"
                                        defaultChecked={collectible["inverse"]}
                                        disabled={!adminPerms}
                                    />
                                </div>
                            </div>
                        </FormatRequirement>
                    )
                })
            }
        </div>
    )
}

function HandleRecords({data, adminPerms}) {
    return (
        <div>
            {
                data.map((record, index) => {
                    return (
                        <FormatRequirement name={`#${index + 1}`}>
                            <div className="grid grid-cols-1 gap-4">
                                <div className={`${textInputDivFormatting} `}>
                                    <label className={labelFormatting} htmlFor={`require_records-${index}-id`}>
                                        Require Record
                                    </label>
                                    <input
                                        className={textInputFormatting}
                                        id={`require_records-${index}-id`}
                                        name={`require_records-${index}-id`}
                                        type="text"
                                        placeholder="required"
                                        required
                                        disabled={!adminPerms}
                                        defaultValue={record["id"]}
                                    />
                                </div>
                                <div className={checkboxInputDivFormatting}>
                                    <label className={labelFormatting} htmlFor={`require_records-${index}-inverse`}>
                                        Invert all settings
                                    </label>
                                    <input
                                        className={checkboxInputFormatting}
                                        id={`require_records-${index}-"inverse`}
                                        name={`require_records-${index}-inverse`}
                                        type="checkbox"
                                        defaultChecked={record["inverse"]}
                                        disabled={!adminPerms}
                                    />
                                </div>
                            </div>
                        </FormatRequirement>
                    )
                })
            }
        </div>
    )
}

function HandleRoles({data, adminPerms}) {
    return (
        <div>
            {
                data.map((role, index) => {
                    return (
                        <FormatRequirement name={`#${index + 1}`}>
                            <div className="grid grid-cols-1 gap-4">
                                <div className={`${textInputDivFormatting} `}>
                                    <label className={labelFormatting} htmlFor={`require_role_ids-${index}-id`}>
                                        Require Role
                                    </label>
                                    <input
                                        className={textInputFormatting}
                                        id={`require_role_ids-${index}-id`}
                                        name={`require_role_ids-${index}-id`}
                                        type="text"
                                        placeholder="required"
                                        required
                                        disabled={!adminPerms}
                                        defaultValue={role["id"]}
                                    />
                                </div>
                                <div className={checkboxInputDivFormatting}>
                                    <label className={labelFormatting} htmlFor={`require_role_ids-${index}-inverse`}>
                                        Invert all settings
                                    </label>
                                    <input
                                        className={checkboxInputFormatting}
                                        id={`require_role_ids-${index}-"inverse`}
                                        name={`require_role_ids-${index}-inverse`}
                                        type="checkbox"
                                        defaultChecked={role["inverse"]}
                                        disabled={!adminPerms}
                                    />
                                </div>
                            </div>
                        </FormatRequirement>
                    )
                })
            }
        </div>
    )
}
