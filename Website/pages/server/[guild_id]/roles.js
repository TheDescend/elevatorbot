import {getSession} from "next-auth/react";
import {getAccessToken} from "../../../lib/http";

export default function Profile() {
  // const { data, error } = useSWR('/api/user', fetcher)
  //
  // if (error) return <div>failed to load</div>
  // if (!data) return <div>loading...</div>
  // return <div>hello {data.name}!</div>
  return <div>placeholder</div>
}
// todo - https://swr.vercel.app/



export async function getServerSideProps(context) {
    const session = await getSession(context)

    return {
        props: {
            token: await getAccessToken(session),
            session: session,
        },
    }
}
