"use client";

import { Raleway } from "next/font/google";
import { motion } from "motion/react";

const raleway = Raleway({
  subsets: ["latin"],
});

export const Navbar = () => {
  return (
    <div className="h-16 bg-cyan-600 flex justify-center shadow-l shadow-white">
      <motion.h1
        initial={{ y: -5, scale: 0.5 }}
        animate={{ y: 0, scale: 1 }}
        transition={{ duration: 0.3 }}
        viewport={{ once: true }}
        className={`${raleway.className} text-center text-4xl py-2`}>
        Versechat
      </motion.h1>
      <motion.p
        initial={{ y: -5, scale: 0.5, opacity:0 }}
        animate={{ y: 0, scale: 1, opacity:1 }}
        transition={{ duration: 0.3, delay:0.3}}
        viewport={{ once: true }}
        className="bg-yellow-300 mb-auto rounded-xl text-black p-1">
        alpha
      </motion.p>
    </div>
  );
};

export default Navbar;