import Link from "next/link";
import {HiChevronRight} from "react-icons/hi";
import {SideBarItems} from "../../data/sideBarItems";

export default function Sidebar() {
    return (
        <div className="bg-gray-500 dark:bg-gray-900 mr-4 hidden md:grid grid-cols-1 w-[350px]">
            <div className="p-6 pl-4 pr-8 gap-4 text-white">
                {
                    Object.keys(SideBarItems).map((name) => {
                        return (
                            <Link href={SideBarItems[name]} passHref>
                                <a className="text-right block pb-4 hover:text-descend flex flex-row group hover:scale-105">
                                    <HiChevronRight className="object-contain h-7 w-7"/>
                                    <p className="group-hover:underline underline-offset-2">
                                        {name}
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
