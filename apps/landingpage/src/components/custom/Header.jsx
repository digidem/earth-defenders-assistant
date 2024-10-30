import React from "react";
import { useTranslation } from "react-i18next";

const Header = ({ theme, themeColors, changeLanguage, languages }) => {
  const { i18n } = useTranslation();

  return (
    <header
      className={`${themeColors[theme].primary} py-4 transition-colors duration-500`}
    >
      <div className="container mx-auto flex flex-col md:flex-row justify-between items-center">
        <div className="text-center md:text-left mb-4 md:mb-0">
          <h1 className="text-2xl font-bold text-white">
            Earth Defenders Assistant
          </h1>
        </div>
        <nav>
          <select
            onChange={(e) => changeLanguage(e.target.value)}
            className={`cursor-pointer ${themeColors[theme].primary} text-white p-2 rounded transition-colors duration-500`}
            value={i18n.language}
          >
            {languages.map((item) => (
              <option key={item.code} value={item.code}>
                {item.name}
              </option>
            ))}
          </select>
        </nav>
      </div>
    </header>
  );
};

export default Header;
