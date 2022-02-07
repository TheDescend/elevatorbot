import Head from 'next/head'
import Footer from "./footer";
import Sidebar from "./sidebar";
import Content from "./content";
import Header from "./header";
import {ToastContainer} from "react-toastify";
import 'react-toastify/dist/ReactToastify.css';


export default function Layout({children, server = null}) {
    const contextClass = {
        success: "bg-blue-600",
        error: "bg-red-600",
        info: "bg-gray-600",
        warning: "bg-orange-400",
        default: "bg-indigo-600",
        dark: "bg-white-600 font-gray-300",
    }

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
                <ToastContainer
                    position="top-right"
                    autoClose={3000}
                    hideProgressBar={false}
                    newestOnTop
                    closeOnClick
                    rtl={false}
                    pauseOnFocusLoss
                    draggable
                    pauseOnHover={false}
                    toastClassName="dark:!bg-slate-700 dark:!text-descend"
                />
                <Header/>
                <div className="flex-grow flex h-full overflow-y-hidden">
                    <Sidebar server={server}/>
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
