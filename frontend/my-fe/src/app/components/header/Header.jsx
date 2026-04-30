"use client";
import { useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";

const Header = () =>{

    const router = useRouter();
    const token = useSyncExternalStore(
        (onStoreChange) => {
            if (typeof window === "undefined") return () => {};
            const handler = () => onStoreChange();
            window.addEventListener("storage", handler);
            // allow same-tab updates to trigger re-render when we dispatch
            window.addEventListener("accessTokenChanged", handler);
            return () => {
                window.removeEventListener("storage", handler);
                window.removeEventListener("accessTokenChanged", handler);
            };
        },
        () => {
            if (typeof window === "undefined") return null;
            return localStorage.getItem("accessToken");
        },
        () => null // server snapshot to avoid hydration mismatch
    );
    const hasToken = !!token;

    const handleLogout = () => {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("user");
        window.dispatchEvent(new Event("accessTokenChanged"));
        router.push("/"); // Navigate to main page
    };

    const handleLogin = () => {
        router.push("/login");
    };

    const handleSignup = () => {
        router.push("/signup");
    };

    return (
        <div className="header">
            <div className="header-top">
                <div className="logo-group">
                    <div className="block-center">
                        <div className="logo">
                            <a href="">
                                <img src="/logo/graph.png" alt="/error/error.png" />
                            </a>
                        </div>
                        <p className="slogan">Ask Me Anything in your ICT283</p>
                    </div>
                </div>

                <div className="group-right">

                    {
                        hasToken ? 
                        (
                        <button className='my-btn my-btn-solid' onClick={handleLogout}>
                            Logout
                        </button>
                        ) : (
                        <>
                            <button className='my-btn my-btn-primary' onClick={handleLogin}>
                                Login
                            </button>
                            <button className='my-btn my-btn-solid' onClick={handleSignup}>
                                Sign Up
                            </button>
                        </>
                        ) 
                    } 

                </div>
            </div>
        </div>
    )
}

export default Header;