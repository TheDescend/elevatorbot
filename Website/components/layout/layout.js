import Head from 'next/head'
import Footer from "./footer";
import Sidebar from "./sidebar";
import Content from "./content";
import Header from "./header";


export default function Layout({children}) {
    return (
        <div>
            <Head>
                <title>ElevatorBot</title>
                <link rel="icon" type="image/png" href="/images/logo_small.png"/>
                <link rel="apple-touch-icon" href="/images/logo_small.png"/>
                <meta charSet="utf-8"/>
                <meta
                    name="description"
                    content="The website for the Discord Bot `ElevatorBot#7635`"
                />
                <meta
                    name="viewport"
                    content="initial-scale=1.0, width=device-width"
                />
            </Head>
            <main className="flex flex-col h-screen bg-descend">
                <Header/>
                <div className="flex-grow flex h-full overflow-y-hidden">
                    <Sidebar/>
                    <div className="flex-grow h-full w-full">
                        <div className="flex flex-col overflow-y-auto scroll-smooth divide-descend divide-y-2 h-full">
                            <Content children={children}/>
                            <Footer/>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    )
}
