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
import Link from "next/link";
import {HiReply} from "react-icons/hi";
import React from "react";


export default function ServerRolePage({token, guild_id, roles}) {
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
    if (roles === null) return <LoadingFailed/>

    return (
        <Layout server={guild}>
            <Title>
                <div className="flex flex-col">
                    <div className="flex flex-row justify-between">
                        {guild.name}'s Roles
                        <span className="text-xs text-descend pr-2 align-top">
                            Discord roles and their names can take up to 30 minutes to update on this page
                        </span>
                    </div>
                    {adminPerms &&
                        <span className="italic text-xs text-descend pt-2">
                            Admin
                        </span>
                    }
                </div>
            </Title>
            <Description>
                <div className="grid grid-flow-row gap-6 pl-2 pt-2">
                    {Array.isArray(roles) &&
                        roles.map((role) => {
                            return (
                                <p>
                                    {role.name}
                                </p>
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
    const roles = await discord.getRoles(guild_id)

    return {
        props: {
            token: await getAccessToken(session),
            session: session,
            guild_id: guild_id,
            roles: roles,
        },
    }
}
