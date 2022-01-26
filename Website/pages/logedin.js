import React from 'react'
import {useSession} from 'next-auth/react'
import Layout from "../components/layout/layout";
import AccessDenied from "../components/auth/accessDenied";

// todo delete
export default function Page() {
    // check if logged in client side
    const { data: session, status } = useSession()

    // If no session exists, display access denied message
    if (status !== "authenticated") {
        return <AccessDenied/>
    }

    // If session exists, display content
    return (
        <Layout>
            <h1>Protected Page</h1>
            <p><strong>Welcome {session.user.name}</strong></p>
        </Layout>
    )
}
