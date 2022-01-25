import {getCommandJson} from '../../lib/commands'
import Layout from "../../components/layout/layout";
import ParseCommand from '../../components/commands'
import Title from "../../components/content/title";
import Description from "../../components/content/description";


export async function getStaticProps() {
    const allCommandData = getCommandJson("commands.json")
    return {
        props: {
            allCommandData
        }
    }
}

// todo add permissions here (sth like the optional thingy)
export default function Commands({allCommandData}) {
    const gridStyle = "grid grid-flow-row gap-2 pl-2 pt-2"
    const gridItemStyle = "p-2 rounded "

    const gridBackground1 = "bg-gradient-to-r from-gray-300 to-gray-400 dark:from-slate-800 dark:to-slate-900"
    const gridBackground2 = "bg-gradient-to-r from-gray-400 to-gray-500 dark:from-slate-700 dark:to-slate-800"

    const commands = Object.keys(allCommandData).map((topic) => {
        return (
            <div className="relative group">
                <div className="absolute -inset-0.5 bg-descend blur opacity-50 group-hover:opacity-100 transition duration-1000 group-hover:duration-200 animate-tilt"/>
                <details className={`relative ${gridItemStyle} ${gridBackground1} marker:text-descend`}>
                    <summary>
                        {topic}
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
                                                        <ParseCommand
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
            </div>
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
