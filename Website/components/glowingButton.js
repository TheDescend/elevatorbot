export default function GlowingButton({children}) {
    return (
        <div className="">
            <div className="grid gap-8 items-start justify-center">
                <div className="relative group">
                    <div
                        className="absolute -inset-0.5 bg-white group-hover:bg-descend rounded-lg blur opacity-30 group-hover:opacity-80 transition duration-1000 group-hover:duration-200 animate-tilt "
                    />
                    <div
                        className="relative px-2 bg-gray-500 dark:bg-gray-900 rounded-lg leading-none flex items-center border-2 border-white hover:border-descend shadow-inner shadow-descend/40 hover:text-descend"
                    >
                        {children}
                    </div>
                </div>
            </div>
        </div>
    )
}
