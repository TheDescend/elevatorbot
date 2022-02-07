import Title from "../components/content/title";
import Description from "../components/content/description";
import Layout from "../components/layout/layout";
import GlowingContainer from "../components/styling/glowingContainer";
import ContentContainer from "../components/styling/container";
import Link from "next/link";


export default function Guides() {
    return (
        <Layout>
            <Title>
                Guides
            </Title>
            <Description>
                <div className="grid grid-flow-row gap-6 pl-2 pt-2">
                    <GuideItem title="Setting up the LFG system">
                        <p>
                            Steps:
                        </p>
                        <ul className="list-decimal ml-8 space-y-2">
                            <li>
                                Designate a channel where LFG event should be posted by using <code>/setup lfg
                                channel</code>
                            </li>
                            <li>
                                <span className="italic text-descend pt-2">
                                    Optional
                                </span>
                                <div>
                                    Do you want ElevatorBot to automatically create and delete voice channels for your
                                    lfg events?
                                    If the answer is yes, designate a category where they should be created by
                                    using <code>/setup lfg voice_category</code>
                                </div>
                            </li>
                            <li>
                                That's it! Type <code>/lfg create</code> to get started
                            </li>
                        </ul>
                    </GuideItem>
                    <GuideItem title="Setting up achievement roles">
                        <p>
                            If you didn't know, there is a deeply customisable achievement role feature.
                        </p>
                        <p>
                            You can link discord roles to basically any Destiny 2 accomplishment and have users show off
                            their impressive feats.
                        </p>
                        <p>
                            <span className="text-descend pr-1">
                                    Example
                            </span>
                            <div>
                                You could give a role to users which have cleared the raid Scourge of the Past
                                twice as a fireteam of two, while not having died and having over 1000 kills each.
                                Oh and the completions need to be on christmas eve 2020, they must never have cleared
                                the raid Last Wish, and they must own the Metro Shift Shader.
                            </div>
                        </p>
                        <p>
                            As I said, very customisable.
                        </p>
                        <p>
                            Steps:
                        </p>
                        <ul className="list-decimal ml-8 space-y-2">
                            <li>
                                Click <Link href="/server/own" passHref>here</Link> and select your server
                            </li>
                            <li>
                                Navigate to the roles page
                            </li>
                            <li>
                                Click on <code>New Role</code> and get creative
                            </li>
                        </ul>
                        <p className="mt-4">
                            <span className="text-descend pr-1">
                                    Note
                            </span>
                            <div>
                                ElevatorBot will automatically apply roles to users every 12 hours. You can get your
                                fancy new role faster by using <code>/roles get</code>
                            </div>
                        </p>
                    </GuideItem>
                    <GuideItem title="Setting up the clan invite button">
                        <p>
                            Do you know the pain of random people requesting to join your fancy Destiny 2 clan, without
                            ever joining your discord even tho that is you only requirement?
                        </p>
                        <p>
                            Well I do. And this system solves it by creating a button in discord which users can press
                            to get an in-game clan invite.
                        </p>
                        <p>
                            Steps:
                        </p>
                        <ul className="list-decimal ml-8 space-y-2">
                            <li>
                                Link your clan to your discord server by using <code>/setup clan link</code>
                            </li>
                            <li>
                                <div>
                                    Designate a channel where the clan invite button should be by using <code>/setup
                                    clan join</code>
                                </div>
                                <div>
                                    Make sure ElevatorBot has write permissions in that channel
                                </div>
                            </li>
                            <li>
                                That's it! Type <code>/lfg create</code> to get started
                            </li>
                        </ul>
                        <p>
                            Now you can go ahead and change your clan to be invite-only.
                        </p>
                    </GuideItem>
                </div>
            </Description>
        </Layout>
    )
}

export function GuideItem({title, children}) {
    return (
        <GlowingContainer>
            <ContentContainer otherStyle={false}>
                <details className="marker:text-descend group">
                    <summary className="group-open:text-descend">
                        {title}
                    </summary>
                    <div>
                        {children}
                    </div>
                </details>
            </ContentContainer>
        </GlowingContainer>
    )
}
