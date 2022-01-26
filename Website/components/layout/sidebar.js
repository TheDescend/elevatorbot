import Link from "next/link";
import {useRouter} from 'next/router'
import {HiChevronRight} from "react-icons/hi";
import {SideBarItems} from "../../data/sideBarItems";

export default function Sidebar() {
    return (
        <div className="hidden big:flex flex-row w-[350px]">
            <div className="flex-grow bg-gradient-to-t from-gray-200 to-gray-300 dark:from-gray-800 dark:to-gray-900 grid grid-cols-1">
                <div className="p-6 pl-4 pr-8 text-gray-900 dark:text-white flex flex-col gap-2">
                    {
                        Object.keys(SideBarItems).map((name) => {
                            if (SideBarItems[name]["is_link"]) {
                                const link = SideBarItems[name]["link"]
                                return (
                                    <Link href={link} passHref>
                                        <a className={`block hover:text-descend flex flex-row group hover:scale-105 ${markActiveLink(link)}`}>
                                            <HiChevronRight className="object-contain h-7 w-7"/>
                                            <p className="group-hover:underline underline-offset-2">
                                                {name}
                                            </p>
                                        </a>
                                    </Link>
                                )
                            } else {
                                return (
                                    <div className="block py-4">
                                        <p className="pb-2 pl-2 font-bold">
                                            {name}
                                        </p>
                                        <div className="grid grid-flow-row gap-2 pl-4">
                                            {
                                                Object.keys(SideBarItems[name]["children"]).map((child_name) => {
                                                    const link = SideBarItems[name]["children"][child_name]
                                                    return (
                                                        <Link href={link} passHref>
                                                            <a className={`block hover:text-descend flex flex-row group hover:scale-105 ${markActiveLink(link)}`}>
                                                                <HiChevronRight className="object-contain h-7 w-7"/>
                                                                <p className="group-hover:underline underline-offset-2">
                                                                    {child_name}
                                                                </p>
                                                            </a>
                                                        </Link>
                                                    )
                                                })
                                            }
                                        </div>
                                    </div>
                                )
                            }
                        })
                    }
                </div>
            </div>
            <div className="bg-descend w-4 blur-sm"/>
        </div>
    )
}

function markActiveLink(path) {
    const {asPath} = useRouter()

    if (asPath === path) {
        return "text-descend"
    } else {
        return ""
    }
}
