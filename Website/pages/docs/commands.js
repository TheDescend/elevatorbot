import {getCommandJson} from '../../lib/commands'
import Layout from "../../components/layout/layout";
import Command from '../../components/commands'
import Title from "../../components/content/title";
import Description from "../../components/content/description";


export async function getStaticProps() {
    const allCommandData = getCommandJson("commands.json")
    const allSubCommandData = getCommandJson("subCommands.json")
    return {
        props: {
            allCommandData, allSubCommandData
        }
    }
}

// todo add permissions here (sth like the optional thingy)
export default function Commands({allCommandData, allSubCommandData}) {
    const gridStyle = "grid grid-flow-row gap-2 pl-2 pt-2"
    const gridItemStyle = "p-2 rounded "

    const gridBackground1 = "bg-gradient-to-r dark:from-slate-800 dark:to-slate-900"
    const gridBackground2 = "bg-gradient-to-r dark:from-slate-700 dark:to-slate-800"

    const commands = Object.keys(allCommandData).map((topic) => {
        return (
            <details className={`${gridItemStyle} ${gridBackground1} marker:text-descend`}>
                <summary>
                    {topic} Commands
                </summary>
                <div className={`${gridStyle}`}>
                    {
                        Object.keys(allCommandData[topic]).map((scope) => {
                            const commandList = allCommandData[topic][scope]

                            return (
                                <details className={`${gridItemStyle} ${gridBackground2}`}>
                                    <summary>
                                        {scope}
                                    </summary>

                                    <div className={`${gridStyle}`}>
                                        {
                                            commandList.map((command) => {
                                                return (
                                                    <Command
                                                        command={command}
                                                        gridStyle={gridStyle}
                                                        gridItemStyle={gridItemStyle}
                                                        gridBackground1={gridBackground1}
                                                        gridBackground2={gridBackground2}
                                                    />
                                                )
                                            })
                                        }
                                    </div>
                                </details>
                            )
                        })
                    }
                </div>
            </details>
        )
    })

    return (
        <Layout>
            <Title title="Commands"/>
            <Description>
                <div className={`${gridStyle} gap-6`}>
                    {commands}
                </div>
            </Description>
        </Layout>
    )
}
