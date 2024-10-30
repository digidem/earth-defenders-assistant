import React from "react";
import { motion } from "framer-motion";

const Footer = ({ theme, themeColors }) => {
  return (
    <footer
      className={`${themeColors[theme].secondary} ${themeColors[theme].textDark} py-8 transition-colors duration-500`}
      style={{
        backgroundImage:
          theme === "default"
            ? "linear-gradient(to right, rgba(34, 197, 94, 0.55), rgba(22, 163, 74, 0.55)), url('https://www.transparenttextures.com/patterns/dark-mosaic.png')"
            : "linear-gradient(to right, rgba(122, 126, 86, 0.55), rgba(246, 125, 49, 0.55)), url('https://www.transparenttextures.com/patterns/dark-mosaic.png')",
        backgroundSize: "contain",
      }}
    >
      <div className="container mx-auto text-center">
        <div
          className={`${themeColors[theme].accent} ${themeColors[theme].textDark} py-2 px-4 inline-block rounded`}
        >
          <a href="https://awana.digital" className="hover:text-green-300">
            Awana Digital
          </a>
        </div>
        <div className="relative mt-4">
          <p className="relative py-4 z-10">
            &copy; {new Date().getFullYear()} Earth Defenders Assistant
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
