import logo from "../../public/images/logo.png"

export default function Sidebar() {
    return (
        <header className="top-0 left-0 bg-gray-900 text-white h-screen sticky">
            <div className="grid grid-cols-1 grid-flow-row p-4 pt-8 gap-4">
                <Link href="/" passHref>
                    <a className="mb-12">
                        <Image
                            src={logo}
                            alt="ElevatorBotLogo"
                        />
                    </a>
                </Link>
                <p className="">
                    test
                </p>
                <p>
                    test2
                </p>
            </div>
        </header>
    )
}

import Image from "next/image";
import Link from "next/link";
