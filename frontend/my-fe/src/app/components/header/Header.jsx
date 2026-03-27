"use client";
import { useEffect, useState } from "react";

import { LuBrainCircuit } from "react-icons/lu"; 

const Header = () =>{
    return (
        <div className="header">
            <div className="header-left">
                <div className="logo-group">
                    <div className="logo">
                        <LuBrainCircuit className='icon'/>;
                    </div>
                </div>
            </div>
        </div>
    )
}