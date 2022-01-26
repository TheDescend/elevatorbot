import {getSession} from "next-auth/react";

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
    // this makes sure that the user is logged in server side and not client side, which is important for those function
    const {req} = context;
    const session = await getSession({req});

    return {
        props: {
            session: session,
        },
    };
}
