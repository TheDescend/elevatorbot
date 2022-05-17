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

    const commands = Object.keys(allCommandData).map((topic) => {
        return (
            <GlowingContainer>
                <ContentContainer otherStyle={false}>
                    <details className="marker:text-descend group">
                        <summary className="group-open:text-descend">
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
                <div className="pt-6 pl-2 italic text-xs text-descend">
                    Unless otherwise specified, commands are not available in DMs.
                </div>
            </Description>
        </Layout>
    )
}
