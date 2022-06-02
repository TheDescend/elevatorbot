import {getSession, useSession} from "next-auth/react";
import request, {discord_fetcher, getAccessToken} from "../../../lib/http";
import AccessDenied from "../../../components/auth/accessDenied";
import useSWR from "swr";
import LoadingFailed from "../../../components/auth/loadingFailed";
import Loading from "../../../components/auth/loading";
import {hasDiscordPermission} from "../../../lib/discordPermission";
import Layout from "../../../components/layout/layout";
import Title from "../../../components/content/title";
import Description from "../../../components/content/description";
import GlowingContainer from "../../../components/styling/glowingContainer";
import ContentContainer from "../../../components/styling/container";
import React, {useState} from "react";
import RoleForm from "../../../components/roleForm";
import {labelFormatting, checkboxInputDivFormatting, checkboxInputFormatting} from "../../../components/roleForm";
import GlowingButton from "../../../components/styling/glowingButton";
import {HiPlus} from "react-icons/hi";
import {toast} from "react-toastify";


export default function ServerRolePage({
                                           token,
                                           guild_id,
                                           discordRoles,
                                           _guildRoles,
                                           destinyActivities,
                                           destinyCollectibles,
                                           destinyTriumphs
                                       }) {

    // check if logged in client side
    const {data: session} = useSession()

    // If no session exists, display access denied message
    if (!session || token === null) {
        return <AccessDenied/>
    }

    // get role data
    _guildRoles = _guildRoles.content.roles
    if (!_guildRoles) return <LoadingFailed/>

    function getAllCategories() {
        let _categoryNames = ["No Category"]
        guildRoles.forEach(function (item) {
            if (!_categoryNames.includes(item["category"])) {
                _categoryNames.push(item["category"])
            }
        })
        return _categoryNames
    }

    let _rolesIds = []
    _guildRoles.forEach(function (item) {
        _rolesIds.push(String(item["role_id"]))
    })

    const [guildRoles, updateGuildRoles] = useState(_guildRoles)
    const [rolesIds, updateRolesIds] = useState(_rolesIds)
    const [categoryNames, updateCategoryNames] = useState(getAllCategories())
    const [enabledCategories, updateEnabledCategories] = useState([])
    const [allCategories, updateAllCategories] = useState(true)

    // get guilds
    const {data, error, mutate} = useSWR(["/users/@me/guilds", token], discord_fetcher)

    if (error) return <LoadingFailed/>
    if (!data) return <Loading/>

    // get guild data
    let guild = null
    data.forEach(function (item, index) {
        if (item.id === guild_id) {
            guild = item
        }
    })
    if (guild === null) return <LoadingFailed/>

    // has admin perms
    const adminPerms = hasDiscordPermission(guild)

    // check roles
    if (discordRoles === null) return <LoadingFailed/>
    let formattedDiscordRoles = {}
    discordRoles.forEach(function (item) {
        if ((item["name"] !== "@everyone") && !(item["managed"])) {
            formattedDiscordRoles[item["id"]] = item
        }
    })

    function createNew() {
        const newRole = {
            "role_id": null,
            "guild_id": guild_id,
            "category": "No Category",
            "deprecated": false,
            "acquirable": true,
            "require_activity_completions": [],
            "require_collectibles": [],
            "require_records": [],
            "require_role_ids": [],
        }
        updateGuildRoles([...guildRoles, newRole])
    }

    async function deleteRole(roleIndex, discordRole) {
        await toast.promise(
            _deleteRole(roleIndex, discordRole),
            {
                pending: {
                    render() {
                        return "Deleting Role..."
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

        const category = guildRoles[roleIndex]["category"]
        if (category !== "No Category" && categoryNames.includes(category)) {
            updateCategoryNames(categoryNames.filter(item => item !== category))
        }
    }

    async function _deleteRole(roleIndex, discordRole) {
        let resultText = "Role has been deleted!"

        // if discordRole is null, we don't need to make an api call since the role is temp
        if (discordRole) {
            // make an api call to delete the role
            const result = await fetch(`/api/roles/delete/${discordRole["id"]}`, {
                body: JSON.stringify({
                    "guild_id": guild_id
                }),
                headers: {
                    'Content-Type': 'application/json'
                },
                method: 'POST'
            })
            resultText = await result.json()
            resultText = resultText.content

            if (result.status !== 200) {
                throw resultText
            }
        }

        updateGuildRoles(x => x.filter((guildRoles, i) => i !== roleIndex))
        return resultText
    }

    const myLabelFormatting = `${labelFormatting} text-xs px-2 text-descend`
    // todo write new category on role create / delete
    return (
        <Layout server={guild}>
            <div className="relative">
                <div className="absolute top-12 right-0">
                    <div className={`${checkboxInputDivFormatting} !justify-end`}>
                        <input
                            className={checkboxInputFormatting}
                            id="category_picker_all"
                            name="category_picker_all"
                            type="checkbox"
                            defaultChecked={allCategories}
                            disabled={false}
                            onChange={() => {
                                updateAllCategories(!allCategories)
                            }}
                        />
                        <label className={myLabelFormatting} htmlFor="category_picker_all">
                            Show all Categories
                        </label>
                    </div>
                    {!allCategories &&
                        <div className="max-h-16 flex flex-grow">
                            <div className={`border rounded p-1 border-descend dark:bg-gray-900 flex flex-col gap-y-2 overflow-y-auto overflow-x-hidden w-full`}>
                                {categoryNames &&
                                    categoryNames.map((name) => {
                                        return (
                                            <div className="flex">
                                                <input
                                                    className="dark:bg-slate-700 rounded-lg border-none text-descend placeholder:italic checked:ring-2 ring-descend"
                                                    id={`category_picker-${name}`}
                                                    name={`category_picker-${name}`}
                                                    type="checkbox"
                                                    disabled={allCategories}
                                                    defaultChecked={enabledCategories.includes(name)}
                                                    onChange={(event) => {
                                                        if (event.target.checked) {
                                                            updateEnabledCategories([name, ...enabledCategories])
                                                        } else {
                                                            updateEnabledCategories(enabledCategories.filter(item => item !== name))
                                                        }
                                                    }}
                                                />
                                                <label className={myLabelFormatting} htmlFor="category_picker_all">
                                                    {name}
                                                </label>
                                            </div>
                                        )
                                    })
                                }
                            </div>
                        </div>
                    }
                </div>
                <Title>
                    <div className="flex flex-col">
                        <div className="flex flex-row justify-between">
                            {guild.name}'s Roles
                            {adminPerms &&
                                <GlowingButton glow={"opacity-20"}>
                                    <button
                                        className=""
                                        type="button "
                                        onClick={() => {
                                            createNew()
                                        }}
                                    >
                                        <div
                                            className="flex flex-row text-white items-center gap-x-1 font-bold text-sm hover:text-descend py-1">
                                            <HiPlus className="object-contain h-4 w-4 "/>
                                            New Role
                                        </div>
                                    </button>
                                </GlowingButton>
                            }
                        </div>
                        {adminPerms &&
                            <span className="italic text-xs text-descend pt-2">
                            Admin
                        </span>
                        }
                        <span className="text-xs text-descend mt-8 border-t w-fit border-descend">
                        Changes done on discord can take up to 30 mins to synchronise
                    </span>
                    </div>
                </Title>
                <Description>
                    <div className="grid grid-flow-row gap-6 pl-2 pt-2">
                        {guildRoles &&
                            guildRoles.map((role, roleIndex) => {
                                if (allCategories || enabledCategories.includes(role["category"])) {
                                    return (
                                        <GlowingContainer>
                                            <ContentContainer>
                                                <RoleForm
                                                    role={role}
                                                    rolesIds={rolesIds}
                                                    updateRolesIds={updateRolesIds}
                                                    guild_id={guild_id}
                                                    discordRoles={formattedDiscordRoles}
                                                    adminPerms={adminPerms}
                                                    destinyActivities={destinyActivities}
                                                    destinyCollectibles={destinyCollectibles}
                                                    destinyTriumphs={destinyTriumphs}
                                                    deleteRole={deleteRole}
                                                    roleIndex={roleIndex}
                                                    updateCategoryNames={updateCategoryNames}
                                                    getAllCategories={getAllCategories}
                                                />
                                            </ContentContainer>
                                        </GlowingContainer>
                                    )
                                } else {
                                    return ""
                                }
                            })
                        }
                    </div>
                </Description>
            </div>
        </Layout>
    )
}

export async function getServerSideProps(context) {
    const session = await getSession(context)
    const {guild_id} = context.query

    const discord = require('../../../lib/discord');
    const discordRoles = await discord.getRoles(guild_id)

    const guildRoles = await request(
        "GET",
        `/destiny/roles/${guild_id}/get/all`
    )

    return {
        props: {
            token: await getAccessToken(session),
            session: session,
            guild_id: guild_id,
            discordRoles: discordRoles,
            _guildRoles: guildRoles,
            destinyActivities: await getDestinyData({key: "destinyActivities", path: "/destiny/activities/get/all"}),
            destinyCollectibles: await getDestinyData({
                key: "destinyCollectibles",
                path: "/destiny/items/collectible/get/all"
            }),
            destinyTriumphs: await getDestinyData({key: "destinyTriumphs", path: "/destiny/items/triumph/get/all"}),
        },
    }
}

async function getDestinyData({key, path}) {
    let value = global.customCache.get(key)

    if (!value) {
        const data = await request(
            "GET",
            path
        )
        value = data.content

        // TTL == 12h
        global.customCache.set(key, value, 43200)
    }

    return value
}
