export default function GlowingContainer({children}) {
    return (
        <div className="relative group">
            <div className="absolute -inset-0.5 bg-descend blur opacity-50 group-hover:opacity-100 transition duration-1000 group-hover:duration-200 animate-tilt"/>
            <div
                className="relative"
            >
                {children}
            </div>
        </div>
    )
}
