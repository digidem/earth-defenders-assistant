import { motion } from "framer-motion";
import { Globe, Mic, Server, Shield } from "lucide-react";
import React from "react";
import { useTranslation } from "react-i18next";

const HowItWorksSection = ({ theme, themeColors }) => {
  const { t } = useTranslation();

  const features = [
    {
      id: "voice",
      icon: <Mic className={`${themeColors[theme].icon} mb-4`} size={48} />,
      title: t("voiceFirstTech"),
      description: t("voiceFirstDesc"),
    },
    {
      id: "offline",
      icon: <Server className={`${themeColors[theme].icon} mb-4`} size={48} />,
      title: t("offlineFirst"),
      description: t("offlineFirstDesc"),
    },
    {
      id: "language",
      icon: <Globe className={`${themeColors[theme].icon} mb-4`} size={48} />,
      title: t("languagePreservation"),
      description: t("languagePreservationDesc"),
    },
    {
      id: "territory",
      icon: <Shield className={`${themeColors[theme].icon} mb-4`} size={48} />,
      title: t("territoryDefense"),
      description: t("territoryDefenseDesc"),
    },
  ];

  return (
    <section
      id="how-it-works"
      className={`pt-32 pb-64 ${themeColors[theme].accent} relative transition-colors duration-500`}
      style={{
        backgroundImage:
          theme === "default"
            ? "linear-gradient(to right, rgba(34, 197, 94, 0.65), rgba(22, 163, 74, 0.65)), url('https://www.transparenttextures.com/patterns/dark-mosaic.png')"
            : "linear-gradient(to right, rgba(122, 126, 86, 0.65), rgba(246, 125, 49, 0.65)), url('https://www.transparenttextures.com/patterns/dark-mosaic.png')",
        backgroundSize: "contain",
      }}
    >
      <div className="container mx-auto">
        <h2
          className={`text-3xl font-bold mb-20 text-center ${themeColors[theme].textDark}`}
        >
          {t("howItWorksTitle")}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature) => (
            <motion.div
              key={feature.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className={`flex flex-col items-center p-6 rounded-lg ${themeColors[theme].card}`}
            >
              {feature.icon}
              <h3
                className={`text-xl font-bold mb-2 ${themeColors[theme].textPrimary}`}
              >
                {feature.title}
              </h3>
              <p className={`text-center ${themeColors[theme].text}`}>
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
      <div className="absolute bottom-0 left-0 w-full overflow-hidden transform rotate-180">
        <svg
          viewBox="0 0 1200 120"
          preserveAspectRatio="none"
          className="relative block w-full h-16"
          role="img"
          aria-labelledby="howItWorksWaveTitle"
        >
          <title id="howItWorksWaveTitle">How It Works Section Wave</title>
          <path
            d="M1200 120L0 16.48V0h1200v120z"
            className={`fill-current ${themeColors[theme].textBackground}`}
          />
        </svg>
      </div>
    </section>
  );
};

export default HowItWorksSection;
