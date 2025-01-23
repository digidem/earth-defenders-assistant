import Contact from "@/components/custom/contact";
import { motion } from "framer-motion";
import React from "react";

const ContactSection = ({ theme, themeColors }) => {
  return (
    <section className={`py-16 ${themeColors[theme].background} relative`}>
      <div className="absolute top-0 left-0 w-full overflow-hidden">
        <svg
          viewBox="0 0 1200 120"
          preserveAspectRatio="none"
          className="relative block w-full h-16"
          style={{ transform: "scaleY(-1)" }}
          role="img"
          aria-labelledby="contactWaveTitle"
        >
          <title id="contactWaveTitle">Contact Section Wave</title>
          <path
            d="M985.66,92.83C906.67,72,823.78,31,743.84,14.19c-82.26-17.34-168.06-16.33-250.45.39-57.84,11.73-114,31.07-172,41.86A600.21,600.21,0,0,1,0,27.35V120H1200V95.8C1132.19,118.92,1055.71,111.31,985.66,92.83Z"
            className={`fill-current ${themeColors[theme].secondary}`}
          />
        </svg>
      </div>
      <div className="container mx-auto pt-20">
        <h2
          className={`text-3xl font-bold mb-12 text-center ${themeColors[theme].textPrimary}`}
        >
          Get in Touch
        </h2>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className={`max-w-md mx-auto ${themeColors[theme].card} rounded-lg p-8 shadow-lg transition-colors duration-500`}
        >
          <Contact theme={themeColors[theme].text} />
        </motion.div>
      </div>
    </section>
  );
};

export default ContactSection;
