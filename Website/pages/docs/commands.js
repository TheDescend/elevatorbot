import {getCommandJson} from '../../lib/commands'
import Layout from "../../components/layout/layout";
import ParseCommand from '../../components/commands'
import Title from "../../components/content/title";
import Description from "../../components/content/description";
import GlowingContainer from "../../components/styling/glowingContainer";
import ContentContainer from "../../components/styling/container";


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
            <GlowingContainer>
                <ContentContainer otherStyle={false}>
                    <details className={`relative marker:text-descend`}>
                        <summary>
                            {topic}
                        </summary>
                        <div className={`${gridStyle}`}>
                            {
                                Object.keys(allCommandData[topic]).map((scope) => {
                                    const commandList = allCommandData[topic][scope]

                                    return (
                                        <ContentContainer otherStyle={true}>
                                            <details>
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
                                                                    otherStyleFirst={false}
                                                                />
                                                            )
                                                        })
                                                    }
                                                </div>
                                            </details>
                                        </ContentContainer>
                                    )
                                })
                            }
                        </div>
                    </details>
                </ContentContainer>
            </GlowingContainer>
        )
    })

    return (
        <Layout>
            <Title>
                Commands
            </Title>
            <Description>
                <div className={`${gridStyle} gap-6`}>
                    {commands}
                </div>
            </Description>
        </Layout>
    )
}
