import {getCommandJson} from '../../lib/commands'
import Layout from "../../components/layout/layout";
import Title from "../../components/content/title";
import Description from "../../components/content/description";
import contextMenuGuide from "../../public/images/docs/contextMenuGuide.png"

import Image from "next/image";
import GlowingContainer from "../../components/styling/glowingContainer";
import ContentContainer from "../../components/styling/container";


export async function getStaticProps() {
    const allContextMenus = getCommandJson("contextMenus.json")

    return {
        props: {
            allContextMenus
        }
    }
}

// todo add permissions here
export default function ContextMenus({allContextMenus}) {
    const gridStyle = "grid grid-flow-row gap-2 pl-2 pt-2"

    const commands = Object.keys(allContextMenus).map((topic) => {
        return (
            <GlowingContainer>
                <ContentContainer otherStyle={false}>
                    <details className={`relative marker:text-descend`}>
                        <summary>
                            {topic}
                        </summary>
                        <div className={`${gridStyle}`}>
                            {
                                Object.keys(allContextMenus[topic]).map((scope) => {
                                    const commandList = allContextMenus[topic][scope]

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
                                                                <ContentContainer otherStyle={false}>
                                                                    <details>
                                                                        <summary>
                                                                            <code className="text-center">
                                                                                {command.name}
                                                                            </code>
                                                                        </summary>
                                                                        <div className={`${gridStyle}`}>
                                                                            <p>
                                                                                {command.description}
                                                                            </p>
                                                                        </div>
                                                                    </details>
                                                                </ContentContainer>
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
                Context Menus
            </Title>
            <Description>
                <div className="flex flex-row gap-x-8">
                    <div className="max-w-lg">
                        To use context menus, you need to right click your target and click on <code>Apps</code>, as can
                        be seen in the picture.
                        You will then see all available commands for your target.
                    </div>
                    <div className="min-w-[200px] w-[200px] not-prose">
                        <Image
                            src={contextMenuGuide}
                            alt="ContextMenuGuide"
                            layout="responsive"
                        />
                    </div>
                </div>
                <div className={`${gridStyle} gap-6 pt-6`}>
                    {commands}
                </div>
            </Description>
        </Layout>
    )
}
