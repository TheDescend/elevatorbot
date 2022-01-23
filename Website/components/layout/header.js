import {FiLogIn} from 'react-icons/fi';
import Link from "next/link";
import DarkModeToggle from "./darkMode";
import {useState} from "react";
import {HiMoon, HiOutlineMenu, HiPlus, HiSun} from "react-icons/hi";
import {useTheme} from "next-themes";
import {SideBarItems} from "../../data/sideBarItems";
import GlowingButton from "../glowingButton";


const loginPath = "/"
const inviteUrl = "some.url/here"


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
            <div className="flex flex-row gap-4">
                <HeaderItemHidden>
                    <DarkModeToggle/>
                </HeaderItemHidden>
                <HeaderItemHidden>
                    <GlowingButton>
                        <a
                            className="hover:text-descend flex flex-col relative w-32 h-10"
                            href={inviteUrl}
                        >
                            <HiPlus className="object-contain h-4 w-4 absolute inset-x-0 top-1 left-[56px]"/>
                            <p className="pl absolute inset-x-0 bottom-1 text-center">
                                Invite To Server
                            </p>
                        </a>
                    </GlowingButton>
                </HeaderItemHidden>
                <HeaderItemHidden>
                    <Link href={loginPath} passHref>
                        <a className="">
                            <GlowingButton>
                                <p className="pr-2">
                                    Login
                                </p>
                                <FiLogIn className="object-contain h-10 w-8 "/>
                            </GlowingButton>
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
                                <p className="mx-2 font-bold hover:underline underline-offset-2">
                                    {theme === "light" ? (
                                        "Switch To Dark Mode"
                                    ) : (
                                        "Switch To Light Mode"
                                    )}
                                </p>
                                {theme === "light" ? (
                                    <HiMoon className="object-contain"/>
                                ) : (
                                    <HiSun className="object-contain"/>
                                )}
                            </div>
                        </button>
                    </div>
                    <div className="block p-2 hover:text-descend hover:underline underline-offset-2">
                        <Link href={loginPath} passHref>
                            <a className="flex flex-row items-center place-content-end">
                                <p className="mx-2 font-bold">
                                    Login With Discord
                                </p>
                                <FiLogIn className="object-contain"/>
                            </a>
                        </Link>
                    </div>
                    <div className="block p-2 hover:text-descend hover:underline underline-offset-2">
                        <Link href={inviteUrl} passHref>
                            <a className="flex flex-row items-center place-content-end">
                                <p className="mx-2 font-bold">
                                    Invite To Discord Server
                                </p>
                                <HiPlus className="object-contain"/>
                            </a>
                        </Link>
                    </div>
                </div>
                <div>
                    {
                        Object.keys(SideBarItems).map((name) => {
                            return (
                                <div className="text-right block p-2 hover:text-descend hover:underline underline-offset-2">
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
