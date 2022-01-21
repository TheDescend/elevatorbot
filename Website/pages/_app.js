import '../styles.css'
import {ThemeProvider} from "next-themes";
import Layout from "../components/layout/layout";

export default function App({Component, pageProps}) {
    return (
        <ThemeProvider forcedTheme={Component.theme || undefined} attribute="class" disableTransitionOnChange={true}
                       defaultTheme="system">
            <Layout>
                <Component {...pageProps} />
            </Layout>
        </ThemeProvider>
    )
}
