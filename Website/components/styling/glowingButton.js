export default function GlowingButton({children, bg = "bg-gray-500 dark:bg-gray-900", glow = "group-hover:opacity-80 group-hover:bg-descend opacity-30"}) {
    return (
        <div className="grid gap-8 items-start items-center group-only-of-type:">
            <div className="relative group">
                <div
                    className={`${glow} absolute -inset-0.5 bg-white rounded-lg blur transition duration-1000 group-hover:duration-200 animate-tilt `}
                />
                <div
                    className={`${bg} relative px-2 rounded-lg leading-none flex items-center border-2 border-white hover:border-descend shadow-inner shadow-descend/40 hover:text-descend`}
                >
                    {children}
                </div>
            </div>
        </div>
    )
}
