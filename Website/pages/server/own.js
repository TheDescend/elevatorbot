import React from 'react'
import {getSession, useSession} from 'next-auth/react'
import Layout from "../../components/layout/layout";
import AccessDenied from "../../components/auth/accessDenied";
import request, {discord_fetcher, getAccessToken} from "../../lib/http";
import useSWR, {useSWRConfig} from "swr";
import Title from "../../components/content/title";
import Loading from "../../components/auth/loading";
import LoadingFailed from "../../components/auth/loadingFailed";
import Description from "../../components/content/description";
import Link from "next/link";
import GlowingContainer from "../../components/styling/glowingContainer";
import ContentContainer from "../../components/styling/container";
import {HiReply} from 'react-icons/hi';
import GlowingButton from "../../components/styling/glowingButton";
import {hasDiscordPermission} from "../../lib/discordPermission";


// todo only show servers where elevator is on Incremental Static Regeneration (ISR)
export default function OwnServers({token, elevatorServers}) {
    // check if logged in client side
    const {data: session} = useSession()

    // If no session exists, display access denied message
    if (!session || token === null) {
        return <AccessDenied/>
    }

    const {cache} = useSWRConfig()

    // get guilds
    const {data, error, mutate} = useSWR(["/users/@me/guilds", token], discord_fetcher)

    if (error) return <LoadingFailed/>
    if (!data) return <Loading/>

    return (
        <Layout>
            <Title>
                <div className="flex flex-row justify-between">
                    Your Servers
                    <GlowingButton bg="bg-gray-100 dark:bg-slate-700">
                        <button
                            className="p-1 text-white text-sm group-hover:text-descend"
                            onClick={async () => {
                                cache.clear()
                                await mutate(["/users/@me/guilds", token])
                            }}>
                            Refresh
                        </button>
                    </GlowingButton>
                </div>
            </Title>
            <Description>
                <p>
                    This are all your servers where ElevatorBot is also a member.
                </p>
                <div className="grid grid-flow-row gap-6 pl-2 pt-2">
                    {Array.isArray(data) ?
                        data.map((guild) => {
                            if (elevatorServers.includes(guild.id)) {
                                const adminPerms = hasDiscordPermission(guild)

                                return (
                                    <GlowingContainer>
                                        <ContentContainer>
                                            <Link href={`/server/${guild["id"]}`} passHref>
                                                <a className="flex flex-row items-center gap-2">
                                                    <HiReply className="object-contain rotate-180"/>
                                                    <p className="group-hover:text-descend">
                                                        {guild["name"]}
                                                    </p>
                                                    {adminPerms &&
                                                        <span className="italic self-center text-xs text-descend pl-2`">
                                                            admin
                                                        </span>
                                                    }
                                                </a>
                                            </Link>
                                        </ContentContainer>
                                    </GlowingContainer>
                                )
                            } else {
                                return ""
                            }
                        })
                        :
                        <p>
                            Discord Error: {data.message}
                        </p>
                    }
                </div>
            </Description>
        </Layout>
    )
}

export async function getServerSideProps(context) {
    const session = await getSession(context)

    return {
        props: {
            token: await getAccessToken(session),
            session: session,
            elevatorServers: await getElevatorServers(),
        },
    }
}


async function getElevatorServers() {
    const key = `elevatorGuilds`

    let value = global.customCache.get(key)

    if (!value){
        const data = await request(
            "GET",
            "/elevator/discord_servers/get/all"
        )

        let guildIds = []
        data.content.guilds.forEach(function (item, index) {
            guildIds.push(item.guild_id.toString())
        })

        value = guildIds
        global.customCache.set(key, value, 600)
    }

    return value
}
