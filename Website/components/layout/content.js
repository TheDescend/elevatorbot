export default function Content({children}) {
    return (
        <div className="
        flex-grow bg-gray-100 dark:bg-slate-700 p-4 pl-6
        prose-headings:text-descend prose-headings:font-bold prose-h1:text-4xl
        prose-p:text-gray-900 dark:prose-p:text-gray-300 prose-p:py-2
        prose-a:text-descend hover:prose-a:text-descend/50
        prose-img:rounded-2xl prose-img:shadow-md
        prose-pre:bg-gray-900 prose-pre:text-descend
        prose-code:bg-descend/50 prose-code:rounded prose-code:font-bold prose-code:text-gray-800 prose-code:px-1
        prose-
        ">
            {children}
        </div>
    )
}
