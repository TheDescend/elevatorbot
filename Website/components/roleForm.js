import GlowingButton from "./styling/glowingButton";
import ContentContainer from "./styling/container";
import {useState} from "react";
import {FiMinusCircle, FiPlusCircle} from "react-icons/fi";
import {toast} from "react-toastify";


const divFormatting = "marker:text-descend"
const summaryFormatting = ""
export const labelFormatting = "px-1"

const _InputFormatting = "dark:bg-gray-900 rounded-lg border-none text-descend placeholder:italic"
const selectInputFormatting = `${_InputFormatting} focus:ring-2 focus:ring-descend required:ring-2 required:ring-red-700 valid:ring-0 mt-1`
const textInputFormatting = `${selectInputFormatting} invalid:text-red-700 `
export const checkboxInputFormatting = `${_InputFormatting} checked:ring-2 ring-descend`

const _InputDivFormatting = "dark:bg-slate-700 flex border-1 p-1 rounded-lg border-white"
const textInputDivFormatting = `${_InputDivFormatting} flex-col justify-between`
export const checkboxInputDivFormatting = `${_InputDivFormatting} flex-row justify-between items-center`


// todo deleting required parts (like a collectible) results in wonky interactions. Fe. if collectible #1 is removed, collectible #2 gets the inputs of #1 since they do not get saved after typing. this might only happen with unsafed form data
export default function RoleForm({
                                     role,
                                     rolesIds,
                                     updateRolesIds,
                                     guild_id,
                                     adminPerms,
                                     discordRoles,
                                     destinyActivities,
                                     destinyCollectibles,
                                     destinyTriumphs,
                                     deleteRole,
                                     roleIndex,
                                     updateCategoryNames,
                                     getAllCategories,
                                 }) {
    const handleForm = async event => {
        await toast.promise(
            _handleForm(event),
            {
                pending: {
                    render() {
                        if (discordRole) {
                            // update
                            return "Updating Role..."
                        } else {
                            // create
                            return "Creating Role..."
                        }
                    },
                },
                success: {
                    render({data}) {
                        return data
                    },
                },
                error: {
                    render({data}) {
                        return data
                    },
                },
            }
        )
    }

    async function _handleForm(event) {
        updateButtonDisabled(true)

        const form = event.target

        let replacedByRoleId = form.replaced_by_role_id.value
        if (replacedByRoleId === "") {
            replacedByRoleId = null
        }

        // correctly write the data
        let data = {
            "role_id": form.role_id.value,
            "guild_id": form.guild_id.value,
            "category": form.category.value,
            "deprecated": form.deprecated.checked,
            "acquirable": form.acquirable.checked,
            "require_activity_completions": [],
            "require_collectibles": [],
            "require_records": [],
            "require_role_ids": [],
            "replaced_by_role_id": replacedByRoleId,
        }
        for (const [_, value] of Object.entries(form)) {
            if (!(value.id)) {
                continue
            }

            const key = value.id

            let parts = []
            let _parts = key.split("-")
            _parts.forEach(function (part) {
                if (isNaN(part)) {
                    parts.push(part)
                } else {
                    parts.push(parseInt(part))
                }
            })

            if (parts.length > 1) {
                if (data[parts[0]].length <= parts[1]) {
                    switch (parts[0]) {
                        case "require_activity_completions":
                            data[parts[0]].push({
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
                                "maximum_allowed_players": 99,
                                "allow_time_periods": [],
                                "disallow_time_periods": [],
                                "inverse": false,
                            })
                            break

                        case "require_role_ids":
                            data[parts[0]].push(null)
                            break

                        default:
                            data[parts[0]].push({
                                "bungie_id": null,
                                "inverse": false,
                            })
                            break
                    }
                }
                switch (parts[2]) {
                    case "allow_time_periods":
                    case "disallow_time_periods":
                        if (data[parts[0]][parts[1]][parts[2]].length <= parts[3]) {
                            data[parts[0]][parts[1]][parts[2]].push({
                                "start_time": null,
                                "end_time": null,
                            })
                        }
                        data[parts[0]][parts[1]][parts[2]][parts[3]][parts[4]] = new Date(value.value)
                        break

                    case "inverse":
                    case "allow_checkpoints":
                    case "require_team_flawless":
                    case "require_individual_flawless":
                        data[parts[0]][parts[1]][parts[2]] = value.checked
                        break

                    case "allowed_activity_hashes":
                        let a = []
                        for (const [_, item] of Object.entries(value.selectedOptions)) {
                            a.push(...item.value.split(","))
                        }
                        data[parts[0]][parts[1]][parts[2]] = a
                        break

                    default:
                        let b = value.valueAsNumber
                        if (isNaN(b)) {
                            b = value.value
                        }
                        if (b === "") {
                            b = null
                        }
                        data[parts[0]][parts[1]][parts[2]] = b
                        break
                }
            }
        }

        event.preventDefault()
        let ogRoleId = null
        let result

        if (discordRole) {
            // update
            ogRoleId = form.original_role_id.value

            result = await fetch(`/api/roles/update/${ogRoleId}`, {
                body: JSON.stringify(data),
                headers: {
                    'Content-Type': 'application/json'
                },
                method: 'POST'
            })

        } else {
            // create
            result = await fetch(`/api/roles/create/`, {
                body: JSON.stringify(data),
                headers: {
                    'Content-Type': 'application/json'
                },
                method: 'POST'
            })

        }

        const json = await result.json()
        updateButtonDisabled(false)

        if (result.status === 200) {
            // update page data
            updateDiscordRole(discordRoles[data["role_id"]])

            updateRoleId(data["role_id"])
            updateCategory(data["category"])
            updateDeprecated(data["deprecated"])
            updateAcquirable(data["acquirable"])
            updateReplacedBy(data["replaced_by_role_id"])

            updateActivities(data["require_activity_completions"])
            updateCollectibles(data["require_collectibles"])
            updateRecords(data["require_records"])
            updateReqRoles(data["require_role_ids"])

            if (!rolesIds.includes(data["role_id"])) {
                updateRolesIds([data["role_id"]], ...rolesIds)
            }
            if (data["role_id"] !== ogRoleId && rolesIds.includes(ogRoleId)) {
                updateRolesIds(rolesIds.filter(item => item !== ogRoleId))
            }

            return json.content
        } else {
            throw json.content
        }
    }

    // if discordRole === null, we know that a new role is being created
    const [discordRole, updateDiscordRole] = useState(discordRoles[role["role_id"]])

    const [roleId, updateRoleId] = useState(role["role_id"])
    const [category, updateCategory] = useState(role["category"])
    const [deprecated, updateDeprecated] = useState(role["deprecated"])
    const [acquirable, updateAcquirable] = useState(role["acquirable"])
    const [replacedBy, updateReplacedBy] = useState(role["replaced_by_role_id"])

    const [activities, updateActivities] = useState(role["require_activity_completions"])
    const [collectibles, updateCollectibles] = useState(role["require_collectibles"])
    const [records, updateRecords] = useState(role["require_records"])
    const [reqRoles, updateReqRoles] = useState(role["require_role_ids"])

    // disable the button while exchanging data with the backend
    const [buttonDisabled, updateButtonDisabled] = useState(false)

    function handleUpdate(key, index = null) {
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

            case "require_activity_completions-allow_time_periods":
                updateActivities(x => x.map((item, i) =>
                    i === index
                        ? {
                            ...item, "allow_time_periods": [...item["allow_time_periods"], {
                                "start_time": null,
                                "end_time": null,
                            }]
                        }
                        : item
                ))
                return

            case "require_activity_completions-disallow_time_periods":
                updateActivities(x => x.map((item, i) =>
                    i === index
                        ? {
                            ...item, "disallow_time_periods": [...item["disallow_time_periods"], {
                                "start_time": null,
                                "end_time": null,
                            }]
                        }
                        : item
                ))
                return

            case "require_role_ids":
                data = null

                updateReqRoles([...reqRoles, data])
                return

            // the others all use the same format
            default:
                data = {
                    "bungie_id": null,
                    "inverse": false,
                }

                switch (key) {
                    case "require_collectibles":
                        updateCollectibles([...collectibles, data])
                        return

                    default:
                        updateRecords([...records, data])
                        return
                }
        }
    }

    function handleDelete(key, index, subIndex = null) {
        switch (key) {
            case "require_activity_completions":
                updateActivities(x => x.filter((activities, i) => i !== index))
                return

            case "require_activity_completions-allow_time_periods":
                updateActivities(x => x.map((item, i) =>
                    i === index
                        ? {
                            ...item,
                            "allow_time_periods": item["allow_time_periods"].filter((periods, i) => i !== subIndex)
                        }
                        : item
                ))
                return

            case "require_activity_completions-disallow_time_periods":
                updateActivities(x => x.map((item, i) =>
                    i === index
                        ? {
                            ...item,
                            "disallow_time_periods": item["disallow_time_periods"].filter((periods, i) => i !== subIndex)
                        }
                        : item
                ))
                return

            case "require_collectibles":
                updateCollectibles(x => x.filter((collectibles, i) => i !== index))
                return

            case "require_records":
                updateRecords(x => x.filter((records, i) => i !== index))
                return

            default:
                updateReqRoles(x => x.filter((reqRoles, i) => i !== index))
                return
        }
    }

    return (
        <details id={discordRole ? discordRole["id"] : "none"} className="marker:text-descend group">
            <summary className="group-open:text-descend">
                {discordRole ?
                    discordRole["name"]
                    :
                    <span className="italic text-gray-500">
                    New Role
                    </span>
                }
            </summary>
            <form onSubmit={handleForm} className="p-2">
                <div className="flex flex-col gap-4 divide-y divide-descend">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="hidden">
                            <input
                                className={textInputFormatting}
                                id="guild_id"
                                name="guild_id"
                                type="text"
                                disabled required
                                value={guild_id}
                            />
                        </div>
                        <div className="hidden">
                            <input
                                className={textInputFormatting}
                                id="original_role_id"
                                name="original_role_id"
                                type="text"
                                disabled
                                value={roleId}
                            />
                        </div>
                        <div className={`${textInputDivFormatting} col-span-full`}>
                            <label className={labelFormatting} htmlFor="category">
                                Role Category
                            </label>
                            <input
                                className={textInputFormatting} id="category" name="category" type="text"
                                placeholder="optional" disabled={!adminPerms}
                                defaultValue={category}
                            />
                        </div>
                        <div className={textInputDivFormatting}>
                            <label className={labelFormatting} htmlFor="role_id">
                                Linked Discord Role
                            </label>
                            <select
                                className={selectInputFormatting} id="role_id" name="role_id"
                                required disabled={!adminPerms}
                            >
                                <option value="" disabled selected className="italic">Select the Role</option>
                                {
                                    Object.keys(discordRoles).map((id) => {
                                        if (id === String(roleId)) {
                                            return (
                                                <option value={id} selected="selected">
                                                    {discordRoles[id]["name"]}
                                                </option>
                                            )
                                        } else {
                                            if (!rolesIds.includes(id)) {
                                                return (
                                                    <option value={id}>
                                                        {discordRoles[id]["name"]}
                                                    </option>
                                                )
                                            }
                                        }
                                    })
                                }
                            </select>
                        </div>
                        <div className={textInputDivFormatting}>
                            <label className={labelFormatting} htmlFor="replaced_by_role_id">
                                Replacement Discord Role
                            </label>
                            <select
                                className={selectInputFormatting} id="replaced_by_role_id" name="replaced_by_role_id"
                                disabled={!adminPerms}
                            >
                                <option value="" disabled className="italic" selected={false}>Select the Role</option>
                                <option value="" className="italic text-white">None</option>
                                {
                                    rolesIds.map((id) => {
                                        if (id !== roleId) {
                                            if (id === String(replacedBy)) {
                                                return (
                                                    <option value={id} selected>
                                                        {discordRoles[id]["name"]}
                                                    </option>
                                                )
                                            } else {
                                                return (
                                                    <option value={id}>
                                                        {discordRoles[id]["name"]}
                                                    </option>
                                                )
                                            }
                                        }
                                    })
                                }
                            </select>
                        </div>
                        <div className={checkboxInputDivFormatting}>
                            <label className={labelFormatting} htmlFor="deprecated">
                                Are any requirements sunset
                            </label>
                            <input
                                className={checkboxInputFormatting} id="deprecated" name="deprecated" type="checkbox"
                                defaultChecked={deprecated} disabled={!adminPerms}
                            />
                        </div>
                        <div className={checkboxInputDivFormatting}>
                            <label className={labelFormatting} htmlFor="acquirable">
                                Allow users to earn this role
                            </label>
                            <input
                                className={checkboxInputFormatting} id="acquirable" name="acquirable" type="checkbox"
                                defaultChecked={acquirable} disabled={!adminPerms}
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
                                    <HandleActivities
                                        data={activities}
                                        adminPerms={adminPerms}
                                        destinyActivities={destinyActivities}
                                        handleDelete={handleDelete}
                                        handleUpdate={handleUpdate}
                                        buttonDisabled={buttonDisabled}
                                    />
                                    {adminPerms &&
                                        <div className="flex">
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    handleUpdate("require_activity_completions")
                                                }}
                                                disabled={buttonDisabled}
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
                                    <HandleCollectibles
                                        data={collectibles}
                                        adminPerms={adminPerms}
                                        destinyCollectibles={destinyCollectibles}
                                        handleDelete={handleDelete}
                                        buttonDisabled={buttonDisabled}
                                    />
                                    {adminPerms &&
                                        <div className="flex">
                                            <button
                                                className=""
                                                type="button"
                                                onClick={() => {
                                                    handleUpdate("require_collectibles")
                                                }}
                                                disabled={buttonDisabled}
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
                                    <HandleRecords
                                        data={records}
                                        adminPerms={adminPerms}
                                        destinyTriumphs={destinyTriumphs}
                                        handleDelete={handleDelete}
                                        buttonDisabled={buttonDisabled}
                                    />
                                    {adminPerms &&
                                        <div className="flex">
                                            <button
                                                className=""
                                                type="button "
                                                onClick={() => {
                                                    handleUpdate("require_records")
                                                }}
                                                disabled={buttonDisabled}
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
                                    <HandleRoles
                                        data={reqRoles}
                                        adminPerms={adminPerms}
                                        discordRoles={discordRoles}
                                        rolesIds={rolesIds}
                                        currentRole={discordRole}
                                        handleDelete={handleDelete}
                                        buttonDisabled={buttonDisabled}
                                    />
                                    {adminPerms &&
                                        <div className="flex">
                                            <button
                                                className=""
                                                type="button "
                                                onClick={() => {
                                                    handleUpdate("require_role_ids")
                                                }}
                                                disabled={buttonDisabled}
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
                                <button
                                    className="p-1 font-bold"
                                    type="submit"
                                    disabled={buttonDisabled}
                                >
                                    {discordRole ? "Update" : "Create"}
                                </button>
                            </GlowingButton>
                            <GlowingButton glow={"opacity-20"}>
                                <button
                                    className="p-1 font-bold"
                                    type="button"
                                    disabled={buttonDisabled}
                                    onClick={async () => {
                                        await deleteRole(roleIndex, discordRole)
                                    }}>
                                    Delete
                                </button>
                            </GlowingButton>
                        </div>
                    }
                </div>
            </form>
        </details>
    )
}

function FormatRequirement({
                               children,
                               name,
                               adminPerms,
                               handleDelete,
                               deleteKey,
                               index,
                               subIndex = null,
                               buttonDisabled
                           }) {
    return (
        <ContentContainer otherStyle={false}>
            <details className={divFormatting}>
                <summary>
                    {name}
                    {adminPerms &&
                        <span className="float-right">
                        <button
                            className="align-middle"
                            type="button"
                            onClick={() => {
                                handleDelete(deleteKey, index, subIndex)
                            }}
                            disabled={buttonDisabled}
                        >
                            <FiMinusCircle className="object-contain hover:text-descend w-5 h-5"/>
                        </button>
                    </span>
                    }
                </summary>
                <div className="grid grid-flow-row gap-2 pl-2 pt-2">
                    {children}
                </div>
            </details>

        </ContentContainer>
    )
}

function HandleActivities({data, adminPerms, destinyActivities, handleDelete, handleUpdate, buttonDisabled}) {
    return (
        <div className="grid grid-flow-row gap-2">
            {
                data.map((activity, index) => {
                    return (
                        <FormatRequirement
                            name={`#${index + 1}`}
                            adminPerms={adminPerms}
                            handleDelete={handleDelete}
                            deleteKey={"require_activity_completions"}
                            index={index}
                            buttonDisabled={buttonDisabled}
                        >
                            <div className="grid grid-cols-2 gap-4">
                                <div className={`${textInputDivFormatting} col-span-full`}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_activity_completions-${index}-allowed_activity_hashes`}>
                                        Allowed Activities
                                    </label>
                                    <select
                                        className={selectInputFormatting}
                                        id={`require_activity_completions-${index}-allowed_activity_hashes`}
                                        name={`require_activity_completions-${index}-allowed_activity_hashes`}
                                        disabled={!adminPerms} required multiple
                                    >
                                        {
                                            destinyActivities["activities"].map((destinyActivity) => {
                                                if (activity["allowed_activity_hashes"].includes(destinyActivity["activity_ids"][0])) {
                                                    return (
                                                        <option value={destinyActivity["activity_ids"]} selected>
                                                            {destinyActivity["name"]}
                                                        </option>
                                                    )
                                                } else {
                                                    return (
                                                        <option value={destinyActivity["activity_ids"]}>
                                                            {destinyActivity["name"]}
                                                        </option>
                                                    )
                                                }
                                            })
                                        }
                                    </select>
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
                                        min="1"
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
                                        min="1"
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
                                        min="1"
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
                                        min="0.01"
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
                                        min="0.01"
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
                                        disabled={!adminPerms}
                                        min="0.01"
                                        step="0.01"
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
                                        min="1"
                                        max="12"
                                        defaultValue={activity["maximum_allowed_players"]}
                                    />
                                </div>
                                <div className={`${textInputDivFormatting} col-span-full`}>
                                    <ContentContainer otherStyle={true}>
                                        <details className={divFormatting}>
                                            <summary className={summaryFormatting}>
                                                Allow only these time periods
                                            </summary>
                                            <div className="grid grid-flow-row gap-2 pl-2 pt-2">
                                                <HandleAllowedTimes
                                                    data={activity["allow_time_periods"]}
                                                    topIndex={index}
                                                    adminPerms={adminPerms}
                                                    destinyActivities={destinyActivities}
                                                    handleDelete={handleDelete}
                                                    buttonDisabled={buttonDisabled}
                                                />
                                                {adminPerms &&
                                                    <div className="flex">
                                                        <button
                                                            type="button"
                                                            onClick={() => {
                                                                handleUpdate("require_activity_completions-allow_time_periods", index)
                                                            }}
                                                            disabled={buttonDisabled}
                                                        >
                                                            <FiPlusCircle
                                                                className="object-contain hover:text-descend w-6 h-6"/>
                                                        </button>
                                                    </div>
                                                }
                                            </div>
                                        </details>
                                    </ContentContainer>
                                </div>
                                <div className={`${textInputDivFormatting} col-span-full`}>
                                    <ContentContainer otherStyle={true}>
                                        <details className={divFormatting}>
                                            <summary className={summaryFormatting}>
                                                Disallow these time periods
                                            </summary>
                                            <div className="grid grid-flow-row gap-2 pl-2 pt-2">
                                                <HandleDisallowedTimes
                                                    data={activity["disallow_time_periods"]}
                                                    topIndex={index}
                                                    adminPerms={adminPerms}
                                                    destinyActivities={destinyActivities}
                                                    handleDelete={handleDelete}
                                                    buttonDisabled={buttonDisabled}
                                                />
                                                {adminPerms &&
                                                    <div className="flex">
                                                        <button
                                                            type="button"
                                                            onClick={() => {
                                                                handleUpdate("require_activity_completions-disallow_time_periods", index)
                                                            }}
                                                            disabled={buttonDisabled}
                                                        >
                                                            <FiPlusCircle
                                                                className="object-contain hover:text-descend w-6 h-6"/>
                                                        </button>
                                                    </div>
                                                }
                                            </div>
                                        </details>
                                    </ContentContainer>
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
                                        id={`require_activity_completions-${index}-inverse`}
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

function HandleAllowedTimes({data, topIndex, adminPerms, handleDelete, buttonDisabled}) {
    return <HandleTimes
        timeType={"allow_time_periods"}
        data={data}
        topIndex={topIndex}
        adminPerms={adminPerms}
        handleDelete={handleDelete}
        buttonDisabled={buttonDisabled}
    />
}

function HandleDisallowedTimes({data, topIndex, adminPerms, handleDelete, buttonDisabled}) {
    return <HandleTimes
        timeType={"disallow_time_periods"}
        data={data}
        topIndex={topIndex}
        adminPerms={adminPerms}
        handleDelete={handleDelete}
        buttonDisabled={buttonDisabled}
    />
}

function HandleTimes({timeType, data, topIndex, adminPerms, handleDelete, buttonDisabled}) {
    return (
        <div className="grid grid-flow-row gap-2">
            {
                data.map((time, index) => {
                    return (
                        <FormatRequirement
                            name={`#${index + 1}`}
                            adminPerms={adminPerms}
                            handleDelete={handleDelete}
                            deleteKey={`require_activity_completions-${timeType}`}
                            index={topIndex}
                            subIndex={index}
                            buttonDisabled={buttonDisabled}
                        >
                            <div className="grid grid-cols-2 gap-4">
                                <div className={textInputDivFormatting}>
                                    <label
                                        className={labelFormatting}
                                        htmlFor={`require_activity_completions-${topIndex}-${timeType}-${index}-start_time`}
                                    >
                                        Start Time
                                    </label>
                                    <input
                                        className={selectInputFormatting}
                                        id={`require_activity_completions-${topIndex}-${timeType}-${index}-start_time`}
                                        name={`require_activity_completions-${topIndex}-${timeType}-${index}-start_time`}
                                        type="datetime-local"
                                        min="2017-10-01T00:00"
                                        max="2050-12-31T00:00"
                                        defaultValue={time["start_time"]}
                                        disabled={!adminPerms}
                                        required
                                    />
                                </div>
                                <div className={textInputDivFormatting}>
                                    <label
                                        className={labelFormatting}
                                        htmlFor={`require_activity_completions-${topIndex}-${timeType}-${index}-end_time`}
                                    >
                                        End Time
                                    </label>
                                    <input
                                        className={selectInputFormatting}
                                        id={`require_activity_completions-${topIndex}-${timeType}-${index}-end_time`}
                                        name={`require_activity_completions-${topIndex}-${timeType}-${index}-end_time`}
                                        type="datetime-local"
                                        min="2017-10-01T00:00"
                                        max="2050-12-31T00:00"
                                        defaultValue={time["end_time"]}
                                        disabled={!adminPerms}
                                        required
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

function HandleCollectibles({data, adminPerms, destinyCollectibles, handleDelete, buttonDisabled}) {
    return (
        <div className="grid grid-flow-row gap-2">
            {
                data.map((collectible, index) => {
                    return (
                        <FormatRequirement
                            name={`#${index + 1}`}
                            adminPerms={adminPerms}
                            handleDelete={handleDelete}
                            deleteKey={"require_collectibles"}
                            index={index}
                            buttonDisabled={buttonDisabled}
                        >
                            <div className="grid grid-cols-1 gap-4">
                                <div className={`${textInputDivFormatting} `}>
                                    <label className={labelFormatting} htmlFor={`require_collectibles-${index}-bungie_id`}>
                                        Require Collectible
                                    </label>
                                    <select
                                        className={selectInputFormatting}
                                        id={`require_collectibles-${index}-bungie_id`}
                                        name={`require_collectibles-${index}-bungie_id`}
                                        disabled={!adminPerms} required
                                    >
                                        <option value="" disabled selected className="italic">
                                            Select the Collectible
                                        </option>
                                        {
                                            destinyCollectibles["collectibles"].map((destinyCollectible) => {
                                                if (collectible["bungie_id"] === (destinyCollectible["reference_id"])) {
                                                    return (
                                                        <option value={destinyCollectible["reference_id"]} selected>
                                                            {destinyCollectible["name"]}
                                                        </option>
                                                    )
                                                } else {
                                                    return (
                                                        <option value={destinyCollectible["reference_id"]}>
                                                            {destinyCollectible["name"]}
                                                        </option>
                                                    )
                                                }
                                            })
                                        }
                                    </select>
                                </div>
                                <div className={checkboxInputDivFormatting}>
                                    <label className={labelFormatting}
                                           htmlFor={`require_collectibles-${index}-inverse`}>
                                        Invert all settings
                                    </label>
                                    <input
                                        className={checkboxInputFormatting}
                                        id={`require_collectibles-${index}-inverse`}
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

function HandleRecords({data, adminPerms, destinyTriumphs, handleDelete, buttonDisabled}) {
    return (
        <div className="grid grid-flow-row gap-2">
            {
                data.map((record, index) => {
                    return (
                        <FormatRequirement
                            name={`#${index + 1}`}
                            adminPerms={adminPerms}
                            handleDelete={handleDelete}
                            deleteKey={"require_records"}
                            index={index}
                            buttonDisabled={buttonDisabled}
                        >
                            <div className="grid grid-cols-1 gap-4">
                                <div className={`${textInputDivFormatting} `}>
                                    <label className={labelFormatting} htmlFor={`require_records-${index}-bungie_id`}>
                                        Require Triumph
                                    </label>
                                    <select
                                        className={selectInputFormatting}
                                        id={`require_records-${index}-bungie_id`}
                                        name={`require_records-${index}-bungie_id`}
                                        disabled={!adminPerms} required
                                    >
                                        <option value="" disabled selected>Select the Triumph</option>
                                        {
                                            destinyTriumphs["triumphs"].map((destinyTriumph) => {
                                                if (record["bungie_id"] === (destinyTriumph["reference_id"])) {
                                                    return (
                                                        <option value={destinyTriumph["reference_id"]} selected>
                                                            {destinyTriumph["name"]}
                                                        </option>
                                                    )
                                                } else {
                                                    return (
                                                        <option value={destinyTriumph["reference_id"]}>
                                                            {destinyTriumph["name"]}
                                                        </option>
                                                    )
                                                }
                                            })
                                        }
                                    </select>
                                </div>
                                <div className={checkboxInputDivFormatting}>
                                    <label className={labelFormatting} htmlFor={`require_records-${index}-inverse`}>
                                        Invert all settings
                                    </label>
                                    <input
                                        className={checkboxInputFormatting}
                                        id={`require_records-${index}-inverse`}
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

function HandleRoles({data, adminPerms, discordRoles, rolesIds, currentRole, handleDelete, buttonDisabled}) {
    let currentRoleId = currentRole
    if (currentRoleId) {
        currentRoleId = currentRole["id"]
    }

    return (
        <div className="grid grid-flow-row gap-2">
            {
                data.map((role, index) => {
                    return (
                        <FormatRequirement
                            name={`#${index + 1}`}
                            adminPerms={adminPerms}
                            handleDelete={handleDelete}
                            deleteKey={"require_role_ids"}
                            index={index}
                            buttonDisabled={buttonDisabled}
                        >
                            <div className="grid grid-cols-1 gap-4">
                                <div className={`${textInputDivFormatting} `}>
                                    <label className={labelFormatting} htmlFor={`require_role_ids-${index}`}>
                                        Require Role
                                    </label>
                                    <select
                                        className={selectInputFormatting}
                                        id={`require_role_ids-${index}`}
                                        name={`require_role_ids-${index}`}
                                        disabled={!adminPerms} required
                                    >
                                        <option value="" disabled selected className="italic">Select the Role</option>
                                        {
                                            rolesIds.map((id) => {
                                                if (id !== currentRoleId) {
                                                    if (id === role) {
                                                        return (
                                                            <option value={id} selected>
                                                                {discordRoles[id]["name"]}
                                                            </option>
                                                        )
                                                    } else {
                                                        return (
                                                            <option value={id}>
                                                                {discordRoles[id]["name"]}
                                                            </option>
                                                        )
                                                    }
                                                }
                                            })
                                        }

                                    </select>
                                </div>
                            </div>
                        </FormatRequirement>
                    )
                })
            }
        </div>
    )
}
