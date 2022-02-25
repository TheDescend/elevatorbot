import request from "../../lib/http";
import Error from 'next/error'
import Layout from "../../components/layout/layout";
import Title from "../../components/content/title";
import Description from "../../components/content/description";

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
        <Layout>
            <Title>
                Successful Registration
            </Title>
            <Description>
                <p>
                    Successfully linked your discord account to destiny user <code>{content["bungie_name"]}</code> on
                    platform <code>{content["system"]}</code>.
                </p>
                {content["user_should_set_up_cross_save"] === true &&
                    <p>
                        You have multiple accounts and do not have cross save set up. If I linked the wrong account, please set it up and then try again. Too be honest, you should set it up anyways. <a href="https://www.bungie.net/7/en/CrossSave">Click here to set it up.</a>
                    </p>
                }
                <p>
                    Come say hi in discord, there may or may not be <a
                    href="https://i.pinimg.com/originals/78/40/41/784041a708117f22ffe0a2bae7e600e2.png">cake.</a>
                </p>
            </Description>
        </Layout>
    )
}
