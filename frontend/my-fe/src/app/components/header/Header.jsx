"use client";
import { useEffect, useState } from "react";

const Header = () =>{
    return (
        <div className="header">
            <div className="header-top">
                <div className="logo-group">
                    <div className="block-center">
                        <div className="logo">
                            <a href="">
                                <img src="/logo/logo.png" alt="/error/error.png" />
                            </a>
                        </div>
                        <p className="slogan">Ask Me Anything in your ICT283</p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Header;