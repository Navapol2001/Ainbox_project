import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import CustomNavbar from "../components/NavBar/Navbar";
import Footer from "../components/Footer/Footer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ainbox 🤖",
  description: "AI In Your Box",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="th">
      <body className={inter.className}>
        <CustomNavbar/>
        {children}
        <Footer/>
      </body>
    </html>
  );
}
