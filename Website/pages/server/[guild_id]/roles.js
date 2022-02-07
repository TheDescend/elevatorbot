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


export default function ServerRolePage({
                                           token,
                                           guild_id,
                                           discordRoles,
                                           guildRoles,
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
    guildRoles = guildRoles.content.roles
    if (!guildRoles) return <LoadingFailed/>

    let _rolesIds = []
    guildRoles.forEach(function (item) {
        _rolesIds.push(String(item["role_id"]))
    })
    const [rolesIds, updateRolesIds] = useState(_rolesIds)

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


    return (
        <Layout server={guild}>
            <Title>
                <div className="flex flex-col">
                    <div className="flex flex-row justify-between">
                        {guild.name}'s Roles

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
                        guildRoles.map((role) => {
                            const discordRole = formattedDiscordRoles[role.role_id]

                            return (
                                <GlowingContainer>
                                    <ContentContainer>
                                        <details className="marker:text-descend group">
                                            <summary className="group-open:text-descend">
                                                {discordRole["name"]}
                                            </summary>
                                            <RoleForm
                                                role={role}
                                                rolesIds={rolesIds}
                                                updateRolesIds={updateRolesIds}
                                                guild_id={guild_id}
                                                discordRole={discordRole}
                                                discordRoles={formattedDiscordRoles}
                                                adminPerms={adminPerms}
                                                destinyActivities={destinyActivities}
                                                destinyCollectibles={destinyCollectibles}
                                                destinyTriumphs={destinyTriumphs}
                                            />
                                        </details>
                                    </ContentContainer>
                                </GlowingContainer>
                            )
                        })
                    }
                </div>
            </Description>
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
            guildRoles: guildRoles,
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
