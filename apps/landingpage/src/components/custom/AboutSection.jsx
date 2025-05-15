import { motion } from "framer-motion";
import React from "react";

const AboutSection = ({ theme, themeColors }) => {
  return (
    <section
      id="about"
      className={`py-32 ${themeColors[theme].background} relative`}
    >
      <div className="container mx-auto">
        <h2
          className={`text-3xl font-bold mb-12 text-center ${themeColors[theme].textPrimary}`}
        >
          About the Project
        </h2>
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <iframe
              src="https://www.buzzsprout.com/2411530/episodes/15878386-introducing-the-earth-defenders-assistant?client_source=small_player&iframe=true"
              loading="lazy"
              width="100%"
              height="200"
              frameBorder="0"
              scrolling="no"
              title="Awana AI Labs, Introducing the Earth Defenders Assistant"
            />
          </motion.div>
        </div>
      </div>
      <div className="absolute bottom-0 left-0 w-full overflow-hidden">
        <svg
          viewBox="0 0 1200 120"
          preserveAspectRatio="none"
          className="relative block w-full h-20"
          style={{ transform: "scaleY(-1)" }}
          role="img"
          aria-labelledby="aboutWaveTitle"
        >
          <title id="aboutWaveTitle">About Section Wave</title>
          <path
            d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z"
            className={`fill-current ${themeColors[theme].textBackground}`}
          />
        </svg>
      </div>
    </section>
  );
};

export default AboutSection;
