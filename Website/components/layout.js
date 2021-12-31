import Head from 'next/head'
import Image from 'next/image'
import Header from "./header";
import Footer from "./footer";
import logo from '../public/images/logo.png'



export const siteTitle = "ElevatorBot"

export default function Layout({children}) {
    return (
        <div>
            <Head>
                <title>{siteTitle}</title>
                <Image src={logo}/>
                <meta
                    name="description"
                    content="The website for the Discord Bot `ElevatorBot#7635`"
                />
                <meta name="og:title" content={siteTitle}/>
            </Head>

            <Header/>

            <main>
                {children}
            </main>

            <Footer/>
        </div>
    )
}
