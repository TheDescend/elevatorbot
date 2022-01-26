import {signIn} from 'next-auth/react'
import Layout from "../layout/layout";
import Title from "../content/title";
import Description from "../content/description";

export default function AccessDenied() {
    return (
        <Layout>
            <Title title={"Access Denied"}/>
            <Description>
                <p>
                    <a href="/api/auth/signin"
                       onClick={(e) => {
                           e.preventDefault()
                           signIn()
                       }}>You must be signed in to view this page</a>
                </p>
            </Description>
        </Layout>
    )
}
