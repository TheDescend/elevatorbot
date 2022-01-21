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
            <main className="flex flex-col h-screen overflow-hidden bg-descend ">
                <Header/>
                <div className="grid grid-cols-8 gap-x-4 ">
                    <Sidebar/>
                    <div className="flex-grow col-span-7 flex flex-col overflow-auto scroll-smooth h-screen divide-descend divide-y-2">
                        <Content children={children}/>
                        <Footer/>
                    </div>
                </div>
            </main>
        </div>
    )
}
