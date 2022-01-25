import '../styles.css'
import {ThemeProvider} from "next-themes";
import {SessionProvider } from 'next-auth/react'

export default function App({Component, pageProps}) {
    return (
        <SessionProvider  session={pageProps.session}>
            <ThemeProvider forcedTheme={Component.theme || undefined} attribute="class" disableTransitionOnChange={true}
                           defaultTheme="dark">
                <Component {...pageProps} />
            </ThemeProvider>
        </SessionProvider >
    )
}
