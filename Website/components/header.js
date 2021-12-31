import Image from "next/image";
import Link from "next/link";

export default function Header() {
    return (
        <header className="fixed top-0">
            <div>
                <Link href="/" passHref>
                    <a>
                        <Image
                            priority
                            src="/images/logo.png"
                            height={108}
                            width={108}
                            alt="logo.png"
                        />
                        <p className="font-bold">
                            Home
                        </p>
                    </a>
                </Link>
            </div>
        </header>
    )
}
