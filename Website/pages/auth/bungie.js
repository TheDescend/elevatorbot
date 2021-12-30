import request from "../../lib/http";
import Error from 'next/error'

export async function getServerSideProps(context) {
    if (!(context.query.code && context.query.state)) {
        return {
            props: {
                status_code: 422,
                content: "Invalid Query Arguments"
            }
        }
    }

    const backendResponse = await request(
        "POST",
        "/auth/bungie",
        {
            code: context.query.code,
            state: context.query.state
        }
    )
    return {
        props: {
            status_code: backendResponse.status_code,
            content: backendResponse.content
        }
    }
}

export default function BungieRegistration({status_code, content}) {
    if (status_code !== 200) {
    return <Error statusCode={status_code} title={content}/>
  }

    return (
        <h1>Successfully registered with the Bungie Name "{content.bungie_name}"</h1>
    )
}
