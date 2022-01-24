import Title from "../components/content/title";
import Description from "../components/content/description";
import Layout from "../components/layout/layout";


export default function Privacy() {
    return (
        <Layout>
            <Title title={"Privacy Policy"}/>
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
                        This site does not use cookies, does not sell any data. Refreshing, right? Tbh, we couldn't even sell your data, since we don't collect any.
                    </p>

                </div>
            </Description>
        </Layout>
    )
}
