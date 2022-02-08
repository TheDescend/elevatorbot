import Title from "../components/content/title";
import Description from "../components/content/description";
import Layout from "../components/layout/layout";
import GlowingContainer from "../components/styling/glowingContainer";
import ContentContainer from "../components/styling/container";
import Link from "next/link";


export default function FAQ() {
    return (
        <Layout>
            <Title>
                FAQ
            </Title>
            <Description>
                <div className="grid grid-flow-row gap-6 pl-2 pt-2">
                    <FAQItem title="What commands does ElevatorBot have?">
                        <p>
                            Click <Link href="/docs/commands" passHref>here</Link> for information about all commands
                        </p>
                        <p>
                            Click <Link href="/docs/contextMenus" passHref>here</Link> for information about all context menus
                        </p>
                    </FAQItem>
                    <FAQItem title="How do I use ElevatorBot in my server?">
                        <p>
                            To invite the official bot to your discord server, click the subtle button at the top of
                            your screen.
                        </p>
                        <p>
                            However, since the bot is fully open source, you can also host him yourself.
                            Check the ReadMe on GitHub for more information.
                        </p>
                    </FAQItem>
                    <FAQItem title="Why are there random words / numbers between colons in my commands?">
                        <p>
                            The <code>:text:</code> fragments are most likely emoji, or a newish discord feature.
                            Either way, it is not being displayed correctly.
                        </p>
                        <p>
                            There are multiple possible fixes:
                        </p>
                        <ul className="list-decimal ml-8 space-y-2">
                            <li>
                                You are running an old version of discord. Please update.
                            </li>
                            <li>
                                The <code>@everyone</code> role does not have the <code>Use External
                                Emoji</code> discord permission.
                            </li>
                        </ul>
                    </FAQItem>
                    <FAQItem title="I have just registered an nothing is working?">
                        <p>
                            Be patient. After registering for the first time, I need to collect all your data which can
                            take quite a while.
                        </p>
                        <p>
                            This can also lead to wrong result when querying Destiny 2 stats.
                        </p>
                    </FAQItem>
                    <FAQItem title="Why are my roles not updating?">
                        <p>
                            The automatic update can take up to 12 hours.
                        </p>
                        <p>
                            If you used <code>/roles get</code> and have not received your new role, you may need to
                            wait for up to an hour.
                            Sadly I can't spam bungies api as much as I want, so you gotta wait until it is your turn.
                        </p>
                    </FAQItem>
                    <FAQItem title="I have this great idea for a new feature!">
                        <p>
                            Great! Would love to hear that.
                        </p>
                        <p>
                            You can either create an issue on GitHub, or join my discord server (which is linked on
                            GitHub) and tell me there.
                        </p>
                    </FAQItem>
                    <FAQItem title="Can I contribute?">
                        <p>
                            Of course!
                        </p>
                        <p>
                            Refer to GitHub for more information. You are more than welcome to just create a PR.
                        </p>
                    </FAQItem>
                    <FAQItem title="I love you!">
                        <p>
                            ❤
                        </p>
                    </FAQItem>
                </div>
            </Description>
        </Layout>
    )
}

export function FAQItem({title, children}) {
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
