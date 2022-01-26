import {signIn} from 'next-auth/react'
import Layout from "../layout/layout";
import Title from "../content/title";
import Description from "../content/description";
import SignInButton from "./signInButton";
import GlowingButton from "../styling/glowingButton";
import {FaDiscord} from "react-icons/fa";

export default function AccessDenied() {
    return (
        <Layout>
            <Title>
                Access Denied
            </Title>
            <Description>
                <p className="mb-8">
                    You must be logged in to view this page.

                </p>
                <SignInButton>
                    <GlowingButton bg="bg-gray-100 dark:bg-slate-700">
                        <div className="flex flex-col items-center">
                            <FaDiscord className="object-contain mt-2"/>
                            <p className="group-hover:text-descend font-bold">
                                Login With Discord
                            </p>
                        </div>
                    </GlowingButton>
                </SignInButton>
            </Description>
        </Layout>
    )
}
