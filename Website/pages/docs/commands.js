import {getCommandJson} from '../../lib/commands'
import Layout from "../../components/layout/layout";
import Command from '../../components/commands'


export async function getStaticProps() {
    const allCommandData = getCommandJson("commands.json")
    const allSubCommandData = getCommandJson("subCommands.json")
    return {
        props: {
            allCommandData, allSubCommandData
        }
    }
}

export default function Commands({allCommandData, allSubCommandData}) {

    const commands = Object.keys(allCommandData).map((topic) => {
        return (
            <li key={topic}>
                {topic}
                <ul>
                    {
                        Object.keys(allCommandData[topic]).map((scope) => {
                            const commandList = allCommandData[topic][scope]

                            return (
                                <li key={scope}>
                                    {scope}
                                    <ul>
                                        {
                                            commandList.map((command) => {
                                                return (
                                                    <Command
                                                        name={command.name}
                                                        description={command.description}
                                                    />
                                                )
                                            })
                                        }
                                    </ul>
                                    <br/>
                                </li>
                            )
                        })
                    }
                </ul>
            </li>
        )
    })

    return (
        <Layout>
            <h1>Commands</h1>
            <section>
                <ul>
                    {commands}
                </ul>
            </section>
        </Layout>
    )
}
