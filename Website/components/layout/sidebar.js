import Link from "next/link";
import {SideBarItems} from "../../data/sideBarItems";

export default function Sidebar() {
    return (
        <div className="bg-gray-500 dark:bg-gray-900 mr-4 hidden md:grid grid-cols-1">
            <div className="p-6 pl-8 pr-8 gap-4 text-white">
                {
                    Object.keys(SideBarItems).map((name) => {
                        return (
                            <div className="text-right block pb-4 hover:text-descend">
                                <Link href={SideBarItems[name]} passHref>
                                    {name}
                                </Link>
                            </div>
                        )
                    })
                }
            </div>
        </div>
    )
}
