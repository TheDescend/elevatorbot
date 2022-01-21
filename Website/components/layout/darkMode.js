import {useTheme} from "next-themes";
import {HiMoon, HiSun} from "react-icons/hi";


export default function DarkModeToggle() {

    const {theme, setTheme} = useTheme()

    return (
        <div className="flex-grow flex flex-row place-content-end mr-8">
            <button
                aria-label="Toggle Dark Mode"
                type="button"
                className="group hover:text-descend pl-2 pr-2"
                onClick={() => {
                    setTheme(theme === 'light' ? 'dark' : 'light')
                }}
            >
                <div className="flex flex-row items-center">
                <span className="invisible w-0 group-hover:visible group-hover:w-auto pr-0 group-hover:pr-2 font-bold">
                   {theme === "light" ? (
                    "Dark Mode"
                ) : (
                    "Light Mode"
                )}
                </span>
                {theme === "light" ? (
                    <HiMoon className="object-contain h-10 w-8 "/>
                ) : (
                    <HiSun className="object-contain h-10 w-8 "/>
                )}
                    </div>
            </button>

        </div>
    );
}
