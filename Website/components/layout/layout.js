import Head from 'next/head'
import Footer from "./footer";
import Sidebar from "./sidebar";
import Content from "./content";


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
            <main className="grid grid-cols-6 grid-rows-1 gap-6 bg-descend">
                <Sidebar/>
                <div className="col-span-5 flex flex-col mr-6">
                    <Content children={children}/>
                    <Footer/>

                </div>
            </main>
        </div>
    )
}
