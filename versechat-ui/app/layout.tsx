import type { Metadata } from "next";
import React from 'react';
import { Geist, Geist_Mono } from "next/font/google";
import { Navbar } from "./navbar/Navbar"
import "./globals.css";
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "VerseChat",
  description: "VerseChat is an AI-powered platform for exploring the Bible and Christianity. Ask questions, discover biblical context, and gain deeper insight into Scripture, Christian teachings, and faith.",
};

interface LayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: Readonly<LayoutProps>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="w-screen h-screen flex flex-col">
        <header className="shrink-0">
          <Navbar />
        </header>
        {children}
      </body>
    </html>
  );
}
