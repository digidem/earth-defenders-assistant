import React from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useTranslation } from "react-i18next";

const CallToAction = ({ theme, themeColors }) => {
  const { t } = useTranslation();

  return (
    <section
      className={`py-16 ${themeColors[theme].secondary} ${themeColors[theme].textDark} relative transition-colors duration-500`}
    >
      <div className="container mx-auto text-center">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-3xl font-bold mb-4"
        >
          {t("readyToDefend")}
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-xl mb-8"
        >
          {t("startUsing")}
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <Button
            variant="secondary"
            size="lg"
            onClick={() => window.open("https://w.app/8A90vk", "_blank")}
          >
            {t("talkToUs")}
          </Button>
        </motion.div>
      </div>
    </section>
  );
};

export default CallToAction;
