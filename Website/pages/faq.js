import Title from "../components/content/title";
import Description from "../components/content/description";
import Layout from "../components/layout/layout";
import GlowingContainer from "../components/styling/glowingContainer";
import ContentContainer from "../components/styling/container";


export default function FAQ() {
    return (
        <Layout>
            <Title>
                FAQ
            </Title>
            <Description>
                <div className="grid grid-flow-row gap-6 pl-2 pt-2">
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
                    <FAQItem title="Why are there random numbers in my commands?">
                        <p>
                            The random number are most likely emoji, or a newish discord feature.
                        </p>
                        <p>
                            There are multiple possible fixes:
                        </p>
                        <ul className="list-decimal ml-8">
                            <li>
                                You are running an old version of discord. Please update.
                            </li>
                            <li>
                                The <code>@everyone</code> role does not have the <code>Use External
                                Emoji</code> discord permission.
                            </li>
                        </ul>
                    </FAQItem>
                    <FAQItem title="Can I contribute?">
                        <p>
                            Of course!
                        </p>
                        <p>
                            Refer to GitHub for more information. You are more than welcome to just create a PR.
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
