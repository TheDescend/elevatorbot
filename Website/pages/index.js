import Title from "../components/content/title";
import Description from "../components/content/description";
import Layout from "../components/layout/layout";


export default function Home() {
    return (
        <Layout>
            <div className="not-prose mb-12 flex flex-row justify-center">
                <img className="max-h-36 " src="/images/logo.png" alt="ElevatorBotLogo"/>
            </div>
            <Title>
                ElevatorBot Welcomes You
            </Title>
            <Description>
                <div>
                    <p>
                        <code>@ElevatorBot#7635</code> is a modern and open source discord bot that can be used to
                        interact with the Destiny 2 API.
                    </p>
                    <p>
                        He was originally created at the start of 2018 for the <a href="https://discord.gg/descend">Descend
                        Discord Server</a> and has <span className="font-bold">greatly</span> expanded in scope since
                        then.
                    </p>
                </div>
            </Description>
        </Layout>
    )
}
