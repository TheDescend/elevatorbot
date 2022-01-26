import React from 'react'
import {getSession, useSession} from 'next-auth/react'
import Layout from "../../components/layout/layout";
import AccessDenied from "../../components/auth/accessDenied";
import {discord_fetcher, getAccessToken} from "../../lib/http";
import useSWR from "swr";
import Title from "../../components/content/title";
import Loading from "../../components/auth/loading";
import LoadingFailed from "../../components/auth/loadingFailed";
import Description from "../../components/content/description";
import Link from "next/link";
import GlowingContainer from "../../components/styling/glowingContainer";
import ContentContainer from "../../components/styling/container";
import {HiReply} from 'react-icons/hi';


export default function OwnServers({token}) {
    // check if logged in client side
    const {data: session} = useSession()

    // If no session exists, display access denied message
    if (!session || token === null) {
        return <AccessDenied/>
    }

    // get guilds
    const {data, error} = useSWR(["/users/@me/guilds", token], discord_fetcher)

    if (error) return <LoadingFailed/>
    if (!data) return <Loading/>

    return (
        <Layout>
            <Title>
                Your Servers
            </Title>
            <Description>
                <div className="grid grid-flow-row gap-6 pl-2 pt-2">
                    {
                        data.map((guild) => {
                            return (
                                <GlowingContainer>
                                    <ContentContainer>
                                        <Link href={`/server/${guild["id"]}`} passHref>
                                            <a className="flex flex-row items-center gap-2">
                                                <HiReply className="object-contain rotate-180"/>
                                                <p className="group-hover:text-descend">
                                                    {guild["name"]}
                                                </p>
                                            </a>
                                        </Link>
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

    return {
        props: {
            token: await getAccessToken(session),
            session: session,
        },
    }
}
