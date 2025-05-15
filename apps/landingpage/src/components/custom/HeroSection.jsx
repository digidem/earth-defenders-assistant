import React from "react";
import { motion } from "framer-motion";
import { LoaderTwo as AnimatedLogo } from "@/components/custom/animated-map";
import { Button } from "@/components/ui/button";
import { Link } from "react-scroll";
import { Play } from "lucide-react";

const HeroSection = ({ theme, themeColors, t }) => {
  return (
    <section
      id="home"
      className={`py-32 relative overflow-hidden ${themeColors[theme].secondary} ${themeColors[theme].textDark} transition-colors duration-500`}
      style={{
        backgroundImage:
          theme === "default"
            ? "linear-gradient(to right, rgba(34, 197, 94, 0.55), rgba(22, 163, 74, 0.55)), url('https://www.transparenttextures.com/patterns/dark-mosaic.png')"
            : "linear-gradient(to right, rgba(122, 126, 86, 0.55), rgba(246, 125, 49, 0.55)), url('https://www.transparenttextures.com/patterns/dark-mosaic.png')",
        backgroundSize: "contain",
      }}
    >
      <div className="container mx-auto text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="flex justify-center pb-8"
        >
          <AnimatedLogo />
        </motion.div>
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-5xl font-bold mb-4 text-white"
        >
          {t("heroTitle")}
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="pb-4 text-xl mb-8 text-white max-w-3xl mx-auto"
        >
          {t("heroDescription")}
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="flex justify-center"
        >
          <Link to="about" smooth={true} duration={500}>
            <Button
              variant="secondary"
              size="lg"
              className={`${themeColors[theme].button} hover:brightness-110 transition-all duration-300 flex items-center gap-2`}
            >
              <Play size={20} />
              {t("listenToPodcast")}
            </Button>
          </Link>
        </motion.div>
      </div>
      <div className="absolute bottom-0 left-0 w-full overflow-hidden">
        <svg
          viewBox="0 0 1200 120"
          preserveAspectRatio="none"
          className="relative block w-full h-20"
          style={{ transform: "scaleY(-1)" }}
        >
          <path
            d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z"
            className={`fill-current ${themeColors[theme].textBackground}`}
          />
        </svg>
      </div>
    </section>
  );
};

export default HeroSection;
