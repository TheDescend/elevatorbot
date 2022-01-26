export default function ContentContainer({children, otherStyle = false}) {
    let style
    if (otherStyle) {
        style = "from-gray-400 to-gray-500 dark:from-slate-700 dark:to-slate-800"
    } else {
        style = "from-gray-300 to-gray-400 dark:from-slate-800 dark:to-slate-900"
    }

    return (
        <div
            className={`${style} p-2 rounded bg-gradient-to-r`}>
            {children}
        </div>
    )
}
