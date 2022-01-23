import {FiLogIn} from 'react-icons/fi';
import Link from "next/link";
import DarkModeToggle from "./darkMode";
import {useState} from "react";
import {HiMoon, HiOutlineMenu, HiSun} from "react-icons/hi";
import {useTheme} from "next-themes";
import {SideBarItems} from "../../data/sideBarItems";


const loginPath = "/"

export default function Header() {
    const [active, setActive] = useState(false);
    const {theme, setTheme} = useTheme()

    const handleClick = () => {
        setActive(!active);
    };

    return (
        <nav className="
            col-span-full flex flex-wrap justify-between space-x-4 p-2 mb-4
            text-white bg-gray-500 dark:bg-gray-900 font-bold
            ">
            <HeaderItemVisible>
                <Link href="/" passHref>
                    <a className="hover:scale-105">
                        <img className="object-contain h-12" src="/images/logo.png" alt="ElevatorBotLogo"/>
                    </a>
                </Link>
            </HeaderItemVisible>
            <div className="flex flex-row">
                <HeaderItemHidden>
                    <DarkModeToggle/>
                </HeaderItemHidden>
                <HeaderItemHidden>
                    <Link href={loginPath} passHref>
                        <a className="flex items-center border-2 rounded-md border-descend pl-2 pr-2 shadow-inner shadow-descend/40 hover:shadow-descend hover:text-descend">
                            <div className="pr-2">
                                Login
                            </div>
                            <FiLogIn className="object-contain h-10 w-8 "/>
                        </a>
                    </Link>
                </HeaderItemHidden>
            </div>
            <div className="flex items-center pl-2 pr-2 hover:text-descend md:hidden">
                <button
                    className={`${!active ? '' : 'text-descend'}`}
                    onClick={handleClick}
                >
                    <HiOutlineMenu className="object-contain w-8 h-8"/>
                </button>
            </div>
            <div
                className={`${active ? '' : 'hidden'} w-full block flex-grow md:hidden divide-y divide-descend font-bold`}
            >
                <div>
                    <div className="text-right block p-2 group hover:text-descend">
                        <button
                            aria-label="Toggle Dark Mode"
                            type="button"
                            onClick={() => {
                                setTheme(theme === 'light' ? 'dark' : 'light')
                            }}
                        >
                            <div className="flex flex-row items-center">
                                {theme === "light" ? (
                                    <HiMoon className="object-contain"/>
                                ) : (
                                    <HiSun className="object-contain"/>
                                )}
                                <p className="ml-1 font-bold">
                                    {theme === "light" ? (
                                        "Switch To Dark Mode"
                                    ) : (
                                        "Switch To Light Mode"
                                    )}
                                </p>
                            </div>
                        </button>
                    </div>
                    <div className="text-right block p-2 hover:text-descend">
                        <Link href={loginPath} passHref>
                            Login With Discord
                        </Link>
                    </div>
                </div>
                <div>
                    {
                        Object.keys(SideBarItems).map((name) => {
                            return (
                                <div className="text-right block p-2 hover:text-descend">
                                    <Link href={SideBarItems[name]} passHref>
                                        {name}
                                    </Link>
                                </div>
                            )
                        })
                    }
                </div>
            </div>
        </nav>
    )
}

function HeaderItemVisible({children}) {
    return (
        <div className="flex items-center space-x-1">
            {children}
        </div>
    )
}

function HeaderItemHidden({children}) {
    return (
        <div className="hidden md:flex items-center space-x-1">
            {children}
        </div>
    )
}
