import { motion } from "framer-motion";
import { Globe, Leaf, Shield } from "lucide-react";
import React from "react";
import { useTranslation } from "react-i18next";

const FeaturesSection = ({ theme, themeColors }) => {
  const { t } = useTranslation();

  const features = [
    {
      id: "mapeo",
      icon: <Globe className={`${themeColors[theme].icon} mb-4`} size={48} />,
      title: t("mapeoIntegration"),
      description: t("mapeoIntegrationDesc"),
    },
    {
      id: "terrastories",
      icon: <Leaf className={`${themeColors[theme].icon} mb-4`} size={48} />,
      title: t("terrastoriesConnection"),
      description: t("terrastoriesConnectionDesc"),
    },
    {
      id: "toolkit",
      icon: <Shield className={`${themeColors[theme].icon} mb-4`} size={48} />,
      title: t("earthDefendersToolkit"),
      description: t("earthDefendersToolkitDesc"),
    },
  ].map((feature) => (
    <motion.div
      key={feature.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay: 0.2 }}
      className={`rounded-lg p-6 text-center shadow-lg hover:shadow-xl transition-shadow duration-300 ${themeColors[theme].card}`}
    >
      {feature.icon}
      <h3
        className={`text-xl font-bold mb-2 ${themeColors[theme].textPrimary}`}
      >
        {feature.title}
      </h3>
      <p className={themeColors[theme].text}>{feature.description}</p>
    </motion.div>
  ));

  return (
    <section
      id="features"
      className={`py-32 ${themeColors[theme].background} relative`}
    >
      <div className="container mx-auto">
        <h2
          className={`text-3xl font-bold mb-12 text-center ${themeColors[theme].textPrimary}`}
        >
          {t("featuresTitle")}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pb-12">
          {features}
        </div>
      </div>
      <div className="absolute bottom-0 left-0 w-full overflow-hidden">
        <svg
          viewBox="0 0 1200 120"
          preserveAspectRatio="none"
          className="relative block w-full h-20"
          style={{ transform: "scaleY(-1)" }}
          role="img"
          aria-labelledby="featuresWaveTitle"
        >
          <title id="featuresWaveTitle">Features Section Wave</title>
          <path
            d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z"
            className={`fill-current ${themeColors[theme].textBackground}`}
          />
        </svg>
      </div>
    </section>
  );
};

export default FeaturesSection;
