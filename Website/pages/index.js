import Link from 'next/link'
import Title from "../components/content/title";


export default function Home() {
    return (
        <div>
            <Title title={"Home"}/>

            <h1 className="title">
                Read{' '}
                <Link href="/training/training">
                    <a>this page!</a>
                </Link>
            </h1>
            <section>
                <p>[Your Self Introduction]</p>
                <p className="font-extrabold text-green-600">
                    (This is a sample website - you’ll be building a site like this on{' '}
                    <a href="https://nextjs.org/learn">our Next.js tutorial</a>.)
                </p>
            </section>
        </div>
    )
}
