import Title from "../components/content/title";
import Description from "../components/content/description";
import Layout from "../components/layout/layout";


export default function Privacy() {
    return (
        <Layout>
            <Title>
                Privacy Policy
            </Title>
            <Description>
                <div>
                    <span className="text-descend">
                        Last Changed 24/01/2022
                    </span>
                    <p>
                        This is rather simple. We save your discord id, what discord server you signed up from and at what time. Additionally, we save your destiny id, what system you play on, and other destiny stats that are accessible through the bungie api.
                    </p>
                    <p>
                        If you want to delete your data, use the <code>/unregister</code> command on discord. You can also contact us on either discord or github.
                    </p>
                    <p>
                        This site uses a cookie to remember your discord authentication, if you did that. The cookie is solely used for that. We have no interest in tracking you and nor do we want to sell your data. Refreshing, right? To be honest, we couldn't even sell your data, since we don't collect any.
                    </p>

                </div>
            </Description>
        </Layout>
    )
}
