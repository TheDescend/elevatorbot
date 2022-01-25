import React from 'react'
import { useSession } from 'next-auth/react'
import Layout from "../components/layout/layout";
import AccessDenied from "../components/accessDenied";


export default function Page () {
  const { data: session } = useSession()

  // If no session exists, display access denied message
  if (!session) { return  <AccessDenied/> }

  // If session exists, display content
  return (
    <Layout>
      <h1>Protected Page</h1>
      <p><strong>Welcome {session.user.name}</strong></p>
    </Layout>
  )
}
