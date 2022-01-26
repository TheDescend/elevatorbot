import React from 'react'
import {getSession, useSession} from 'next-auth/react'
import Layout from "../../components/layout/layout";
import AccessDenied from "../../components/auth/accessDenied";
import {discord_fetcher, getAccessToken} from "../../lib/http";
import useSWR from "swr";
import {ImSpinner2} from "react-icons/im";
import Title from "../../components/content/title";
import Loading from "../../components/auth/loading";
import LoadingFailed from "../../components/auth/loadingFailed";
import Description from "../../components/content/description";


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
                {
                 Object.keys(data).map((key) => {
                    return (
                        <p>
                            {key}
                        </p>
                    )
                })
            }
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
