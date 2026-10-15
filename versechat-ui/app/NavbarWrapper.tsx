"use client";

import {usePathname} from "next/navigation";
import Navbar from './navbar/Navbar'
import React from "react";

const NavbarWrapper: React.FC = () => {
    const pathname = usePathname();

    const hideNavBar = ["/", "/login"].includes(pathname);

    if (hideNavBar) return null;
    return <Navbar/>;
}

export default NavbarWrapper;