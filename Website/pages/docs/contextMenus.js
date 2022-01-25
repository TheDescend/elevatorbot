import {getCommandJson} from '../../lib/commands'
import Layout from "../../components/layout/layout";
import Title from "../../components/content/title";
import Description from "../../components/content/description";
import contextMenuGuide from "../../public/images/docs/contextMenuGuide.png"

import Image from "next/image";



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
    const gridItemStyle = "p-2 rounded "

    const gridBackground1 = "bg-gradient-to-r from-gray-300 to-gray-400 dark:from-slate-800 dark:to-slate-900"
    const gridBackground2 = "bg-gradient-to-r from-gray-400 to-gray-500 dark:from-slate-700 dark:to-slate-800"

    const commands = Object.keys(allContextMenus).map((topic) => {
        return (
            <details className={`${gridItemStyle} ${gridBackground1} marker:text-descend`}>
                <summary>
                    {topic}
                </summary>
                <div className={`${gridStyle}`}>
                    {
                        Object.keys(allContextMenus[topic]).map((scope) => {
                            const commandList = allContextMenus[topic][scope]

                            return (
                                <details className={`${gridItemStyle} ${gridBackground2}`}>
                                    <summary>
                                        {scope}
                                    </summary>

                                    <div className={`${gridStyle}`}>
                                        {
                                            commandList.map((command) => {
                                                return (
                                                    <details className={`${gridItemStyle} ${gridBackground1}`}>
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
                <div className="flex flex-row gap-x-8 prose-img:rounded-none">
                    <div className="max-w-lg">
                        To use context menus, you need to right click your target and click on <code>Apps</code>, as can
                        be seen in the picture.
                        You will then see all available commands for your target.
                    </div>
                    <div className="min-w-[200px] w-[200px]">
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
