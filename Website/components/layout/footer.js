import Link from "next/link";

export default function Footer() {
    return (
        <footer className="
            p-2 pt-6
            bg-gray-500 dark:bg-gray-900 text-center text-white dark:text-gray-400 font-bold text-sm
        ">
            <div className="flex flex-col space-y-4">
                <div className="flex flex-row justify-center space-x-12">
                    <Link href="/privacy" passHref>
                        Privacy Policy
                    </Link>
                    <a target="_blank" rel="noopener noreferrer" href="https://github.com/LukasSchmid97/elevatorbot">
                        GitHub
                    </a>
                </div>
                <p className="text-xs text-right text-gray-400 dark:text-gray-500">
                    © 2022 Kigstn
                </p>
            </div>
        </footer>
    )
}
