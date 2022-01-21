import {FiLogIn} from 'react-icons/fi';
import Link from "next/link";
import DarkModeToggle from "./darkMode";

export default function Header() {
    return (
        <header className="col-span-full text-gray-300 bg-gray-900 flex justify-between p-2 pl-3 pr-3 font-bold">
            <Link href="/" passHref>
                <a className="hover:scale-105">
                    <img className="object-contain h-12" src="/images/logo.png" alt="ElevatorBotLogo"/>

                </a>
            </Link>
            <DarkModeToggle/>
            <Link href="/" passHref>
                <a className="flex items-center border-2 rounded-md border-descend pl-2 pr-2 shadow-inner shadow-descend/40 hover:shadow-descend hover:text-descend">
                    <div className="pr-2">
                        Login
                    </div>
                    <FiLogIn className="object-contain h-10 w-8 "/>

                </a>
            </Link>

        </header>
    )
}
