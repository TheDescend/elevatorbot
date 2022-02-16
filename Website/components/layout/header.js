import {FiLogIn, FiLogOut} from 'react-icons/fi';
import Link from "next/link";
import DarkModeToggle from "./darkMode";
import {useState} from "react";
import {HiMoon, HiOutlineMenu, HiPlus, HiSun} from "react-icons/hi";
import {FaDiscord} from 'react-icons/fa';
import {useTheme} from "next-themes";
import {SideBarItems} from "../../data/sideBarItems";
import GlowingButton from "../styling/glowingButton";
import SignInButton from "../auth/signInButton";
import {useSession} from "next-auth/react";
import SignOutButton from "../auth/signOutButton";
import Image from "next/image";


const loginPath = "/auth/discord"
const inviteUrl = "https://www.urbandictionary.com/define.php?term=soon%20%28tm%29"

export default function Header() {
    // check if logged in client side
    const {data: session, status} = useSession()

    const [active, setActive] = useState(false);
    const {theme, setTheme} = useTheme()

    const handleClick = () => {
        setActive(!active);
    };

    return (
        <div className="flex flex-col">
            <nav className="
            col-span-full flex flex-wrap justify-between space-x-4 p-2
            text-white bg-gray-500 dark:bg-gray-900 font-bold
            ">
                <HeaderItemVisible>
                    <Link href="/" passHref>
                        <a className="hover:scale-105">
                            <img className="object-contain h-12" src="/images/logo.png" alt="ElevatorBotLogo"/>
                        </a>
                    </Link>
                </HeaderItemVisible>
                {status === "authenticated" &&
                    <div className="flex flex-row items-center gap-x-1 relative">
                        <Image
                            src={session.user.image}
                            alt="DiscordAvatar"
                            layout="fixed"
                            width={"30px"}
                            height={"30px"}
                            className="[clip-path:circle()]"
                        />
                        <p className="text-descend">
                            {session.user.name}
                        </p>

                    </div>
                }
                <HeaderItemHidden>
                    <div className="flex flex-row gap-4">
                        <DarkModeToggle/>
                        <GlowingButton>
                            <a
                                className="hover:text-descend flex flex-col relative w-32 h-10"
                                target="_blank" rel="noopener noreferrer" href={inviteUrl}
                            >
                                <HiPlus className="object-contain h-4 w-4 absolute inset-x-0 top-1 left-[56px]"/>
                                <p className="pl absolute inset-x-0 bottom-1 text-center font-bold">
                                    Invite To Server
                                </p>
                            </a>
                        </GlowingButton>
                        <GlowingButton>
                            {status !== "authenticated" ?
                                <SignInButton>
                                    <div className="flex flex-row">
                                        <div className="relative w-12">
                                            <FaDiscord className="object-contain absolute inset-x-0 top-1 left-[16px]"/>
                                            <p className="absolute text-center bottom-1 font-bold inset-x-0">
                                                Login
                                            </p>
                                        </div>
                                        <FiLogIn className="object-contain h-10 w-8 "/>
                                    </div>
                                </SignInButton>
                                :
                                <SignOutButton>
                                    <div className="flex flex-row items-center">
                                        <p className="pr-2 font-bold">
                                            Logout
                                        </p>
                                        <FiLogOut className="object-contain h-10 w-8"/>
                                    </div>
                                </SignOutButton>
                            }
                        </GlowingButton>
                    </div>
                </HeaderItemHidden>
                <div className="flex items-center pl-2 pr-2 hover:text-descend big:hidden">
                    <button
                        className={`${!active ? '' : 'text-descend'}`}
                        onClick={handleClick}
                    >
                        <HiOutlineMenu className="object-contain w-8 h-8"/>
                    </button>
                </div>
                <div
                    className={`${active ? '' : 'hidden'} w-full block flex-grow big:hidden divide-y divide-descend font-bold`}
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
                        <div className="text-right block p-2 hover:text-descend hover:underline underline-offset-2 ">
                            {status !== "authenticated" ?
                                <SignInButton>
                                    <div className="flex flex-row items-center">
                                        <p className="mx-2 font-bold">
                                            Login With Discord
                                        </p>
                                        <FiLogIn className="object-contain"/>
                                    </div>
                                </SignInButton>
                                :
                                <SignOutButton>
                                    <div className="flex flex-row items-center">
                                        <p className="mx-2 font-bold">
                                            Logout
                                        </p>
                                        <FiLogOut className="object-contain"/>
                                    </div>
                                </SignOutButton>
                            }
                        </div>
                        <div className="block p-2 hover:text-descend hover:underline underline-offset-2">
                            <a
                                target="_blank" rel="noopener noreferrer" href={inviteUrl}
                                className="flex flex-row items-center place-content-end"
                            >
                                <p className="mx-2 font-bold">
                                    Invite To Discord Server
                                </p>
                                <HiPlus className="object-contain"/>
                            </a>
                        </div>
                    </div>
                    <div>
                        {
                            Object.keys(SideBarItems).map((name) => {
                                if (SideBarItems[name]["is_link"]) {
                                    return (
                                        <Link href={SideBarItems[name]} passHref>
                                            <a className="text-right block p-2 hover:text-descend hover:underline underline-offset-2">
                                                {name}
                                            </a>
                                        </Link>
                                    )
                                } else {
                                    return Object.keys(SideBarItems[name]["children"]).map((child_name) => {
                                        return (
                                            <Link href={SideBarItems[name]["children"][child_name]} passHref>
                                                <a className="text-right block p-2 hover:text-descend hover:underline underline-offset-2">
                                                    {name} | {child_name}
                                                </a>
                                            </Link>
                                        )
                                    })
                                }
                            })
                        }

                    </div>
                </div>
            </nav>
            <div className="bg-descend h-4 blur-sm"/>
        </div>
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
        <div className="hidden big:flex items-center space-x-1">
            {children}
        </div>
    )
}
