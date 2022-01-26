import {signOut} from "next-auth/react";

export default function SignOutButton({children}) {
    return (
        <button onClick={() => signOut()}>
            {children}
        </button>
    )
}
