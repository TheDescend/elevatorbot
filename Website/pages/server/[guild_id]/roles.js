import {getSession, useSession} from "next-auth/react";
import {discord_fetcher, getAccessToken} from "../../../lib/http";
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
import React from "react";
import RoleForm from "../../../components/roleForm";


export default function ServerRolePage({token, guild_id, discordRoles, guildRoles}) {
    // check if logged in client side
    const {data: session} = useSession()

    // If no session exists, display access denied message
    if (!session || token === null) {
        return <AccessDenied/>
    }

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

    // todo temp
    guildRoles = [{
        "role_name": "test",
        "role_data": {
            "category": "Destiny Roles",
            "deprecated": false,
            "acquirable": true,
            "require_activity_completions": [
            ],
            "require_collectibles": [],
            "require_records": [],
            "require_role_ids": [],
            "replaced_by_role_id": 12345
        }
    }]

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
                            Changes done on discord can take up to 30 to synchronise
                        </span>
                </div>
            </Title>
            <Description>
                <div className="grid grid-flow-row gap-6 pl-2 pt-2">
                    {guildRoles &&
                        guildRoles.map((role) => {
                            return (
                                <GlowingContainer>
                                    <ContentContainer>
                                        <details className="marker:text-descend group">
                                            <summary className="group-open:text-descend">
                                                {role["role_name"]}
                                            </summary>
                                            <RoleForm
                                                role={role}
                                                adminPerms={adminPerms}
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

    const guildRoles = null

    return {
        props: {
            token: await getAccessToken(session),
            session: session,
            guild_id: guild_id,
            discordRoles: discordRoles,
            guildRoles: guildRoles
        },
    }
}
