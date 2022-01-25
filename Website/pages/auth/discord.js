// https://dev.to/ndom91/adding-authentication-to-an-existing-serverless-next-js-app-in-no-time-with-nextauth-js-192h

import { getProviders, signIn } from "next-auth/react"
import Layout from "../../components/layout/layout";
import Title from "../../components/content/title";
import Description from "../../components/content/description";

export default function SignIn({ providers }) {
  return (
    <Layout>
        <Title title={"Log In With Discord"}/>
            <Description>
                <p>
                    Click the button to log in with discord
                </p>
                      {Object.values(providers).map((provider) => (
        <div key={provider.name}>
          <button onClick={() => signIn(provider.id)}>
            Sign in with {provider.name}
          </button>
        </div>
      ))}
            </Description>


    </Layout>
  )
}

// This is the recommended way for Next.js 9.3 or newer
export async function getServerSideProps(context) {
  const providers = await getProviders()
  return {
    props: { providers },
  }
}
