import {getCommandJson} from '../../lib/commands'
import Layout from "../../components/layout";
import utilStyles from '../../styles/utils.module.css'
import Command from '../../components/Commands'


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
            <li className={utilStyles.listItem} key={topic}>
                {topic}
                <ul className={utilStyles.list}>
                    {
                        Object.keys(allCommandData[topic]).map((scope) => {
                            const commandList = allCommandData[topic][scope]

                            return (
                                <li className={utilStyles.listItem} key={scope}>
                                    {scope}
                                    <ul className={utilStyles.list}>
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
            <section className={`${utilStyles.headingMd} ${utilStyles.padding1px}`}>
                <ul className={utilStyles.list}>
                    {commands}
                </ul>
            </section>
        </Layout>
    )
}
