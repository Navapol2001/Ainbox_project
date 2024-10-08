"use client";
import { ainboxData } from "../../store/HomeData";
import Image from "next/image";
import { Link } from "react-scroll";
import React, { useState } from "react";
import { IoMenuOutline } from "react-icons/io5";
import { IoClose } from "react-icons/io5";

const CustomNavbar: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const textColorActive = "text-orange-500";
  const styleBtnNavbar = "hover:text-orange-600 cursor-pointer";
  const frontendUrl = process.env.NEXT_PUBLIC_FRONTEND_URL || "http://localhost:3001";


  const loginHandle = () => {
    if (typeof window !== "undefined") {
      window.location.href = `${frontendUrl}/login`; //จะทำการจัดเก็บไว้ใน .env ภายหลัง
    }
  }

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
    loginHandle();
  };

  return (
    <nav className="h-[70px] flex justify-between items-center w-full fixed top-0 z-[1000] bg-[#ffffff] shadow-sm px-2 lg:px-8">
      <Image src={ainboxData.img.logo} alt="logo" width={150} height={150} />
      <div className="hidden md:flex topic lg:text-[20px] justify-evenly w-[60%] md:w-1/2">
        <Link
          to="home"
          spy={true}
          smooth={true}
          duration={500}
          className={styleBtnNavbar}
          activeClass={textColorActive}
        >
          บริการของเรา
        </Link>
        <Link
          to="example"
          spy={true}
          smooth={true}
          duration={500}
          className={styleBtnNavbar}
          activeClass={textColorActive}
        >
          ตัวอย่างการใช้งาน
        </Link>
        <Link
          to="faq"
          spy={true}
          smooth={true}
          duration={500}
          className={styleBtnNavbar}
          activeClass={textColorActive}
        >
          คำถามยอดนิยม
        </Link>
        <Link
          to="price"
          spy={true}
          smooth={true}
          duration={500}
          className={styleBtnNavbar}
          activeClass={textColorActive}
        >
          ราคา
        </Link>
      </div>
      <button className="hidden md:block font-semibold text-[19px] py-1.5 px-4 rounded-xl text-white bg-orange-600 hover:scale-[1.1] " onClick={loginHandle}>
        เข้าสู่ระบบ
      </button>
      <button
        className="md:hidden text-[24px] cursor-pointer"
        onClick={toggleMenu}
      >
        <IoMenuOutline size={40} className="text-[#333]" />
      </button>

      {isMenuOpen && (
        <div className="fixed inset-0 z-[2000] backdrop-blur-2xl flex justify-center items-center">
          <div className=" p-8 w-full h-1/2 text-center">
            <button
              className="absolute top-4 right-4 text-2xl"
              onClick={toggleMenu}
            >
              <IoClose size={45} color="#555" />
            </button>
            <nav className="flex flex-col space-y-4 text-[32px] mt-[-50px]">
              <Link
                to="home"
                spy={true}
                smooth={true}
                duration={500}
                className={styleBtnNavbar}
                activeClass={textColorActive}
                onClick={toggleMenu}
              >
                บริการของเรา
              </Link>
              <Link
                to="example"
                spy={true}
                smooth={true}
                duration={500}
                className={styleBtnNavbar}
                activeClass={textColorActive}
                onClick={toggleMenu}
              >
                ตัวอย่างการใช้งาน
              </Link>
              <Link
                to="faq"
                spy={true}
                smooth={true}
                duration={500}
                className={styleBtnNavbar}
                activeClass={textColorActive}
                onClick={toggleMenu}
              >
                คำถามยอดนิยม
              </Link>
              <Link
                to="price"
                spy={true}
                smooth={true}
                duration={500}
                className={styleBtnNavbar}
                activeClass={textColorActive}
                onClick={toggleMenu}
              >
                ราคา
              </Link>
              <div className="flex item-center justify-center">
                <button
                  className="mt-12 w-[80%] text-[25px] py-2 px-4 rounded-xl text-white bg-gradient-to-b from-[#FB8854] to-[#F9373C] hover:scale-[1.1]"
                  onClick={toggleMenu}
                >
                  เข้าสู่ระบบ
                </button>
              </div>
            </nav>
          </div>
        </div>
      )}
    </nav>
  );
};

export default CustomNavbar;
