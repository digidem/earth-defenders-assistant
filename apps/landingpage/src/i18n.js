import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: {
          // English translations
          heroTitle: "Empower Indigenous Communities with AI",
          heroDescription:
            "Harnessing offline-first technology to preserve languages, protect territories, and ensure data sovereignty for communities on the front lines of climate justice.",
          listenToPodcast: "Listen to Podcast",
          aboutTitle: "About the Project",
          howItWorksTitle: "How It Works",
          featuresTitle: "Key Features",
          projectOverviewTitle: "Project Overview",
          projectObjectives: "Project Objectives",
          expectedOutcomes: "Expected Outcomes",
          readyToDefend: "Ready to Defend the Earth?",
          startUsing: "Start using Earth Defenders Assistant today!",
          talkToUs: "Talk to us",
          getInTouch: "Get in Touch",
          // Add more translations here
          voiceFirstTech: "Voice-First Technology",
          voiceFirstDesc: "Natural voice interactions in Indigenous languages",
          offlineFirst: "Offline-First Solutions",
          offlineFirstDesc: "Operate without internet using local servers",
          languagePreservation: "Language Preservation",
          languagePreservationDesc: "Train AI models for Indigenous languages",
          territoryDefense: "Territory Defense",
          territoryDefenseDesc:
            "Secure tools for documenting sensitive information",
          mapeoIntegration: "Mapeo Integration",
          mapeoIntegrationDesc:
            "Seamlessly create and manage geo-observations through WhatsApp",
          terrastoriesConnection: "Terrastories Connection",
          terrastoriesConnectionDesc:
            "Share and preserve your community's stories with ease",
          earthDefendersToolkit: "Earth Defenders Toolkit",
          earthDefendersToolkitDesc:
            "Access a wealth of resources and tools for environmental protection",
          enhanceAccessibility:
            "Enhance accessibility through voice-first technology",
          implementOffline: "Implement offline-first, community-led solutions",
          trainAI: "Train AI models for language preservation",
          developTools: "Develop robust project management tools",
          supportSustainable:
            "Support sustainable territory defense and cultural preservation",
          integrateWhatsApp:
            "Integrate with WhatsApp for easy access and communication",
          empoweredCommunities: "Empowered Indigenous communities",
          languageCulturalPreservation: "Language and cultural preservation",
          increasedAccessibility: "Increased accessibility to technology",
          dataSovereignty: "Data sovereignty for communities",
          effectiveProjectManagement:
            "Effective project management capabilities",
          simplifiedCommunication:
            "Simplified communication through WhatsApp integration",
          name: "Name",
          email: "Email",
          message: "Message",
          send: "Send",
        },
      },
      es: {
        translation: {
          // Spanish translations
          heroTitle: "Empoderar a las Comunidades Indígenas con IA",
          heroDescription:
            "Aprovechando la tecnología sin conexión para preservar idiomas, proteger territorios y garantizar la soberanía de datos para las comunidades en primera línea de la justicia climática.",
          listenToPodcast: "Escuchar el Podcast",
          aboutTitle: "Sobre el Proyecto",
          howItWorksTitle: "Cómo Funciona",
          featuresTitle: "Características Principales",
          projectOverviewTitle: "Resumen del Proyecto",
          projectObjectives: "Objetivos del Proyecto",
          expectedOutcomes: "Resultados Esperados",
          readyToDefend: "¿Listo para Defender la Tierra?",
          startUsing: "¡Comienza a usar Earth Defenders Assistant hoy!",
          talkToUs: "Habla con nosotros",
          getInTouch: "Ponte en Contacto",
          // Add more translations here
          voiceFirstTech: "Tecnología de Voz Primero",
          voiceFirstDesc: "Interacciones de voz naturales en lenguas indígenas",
          offlineFirst: "Soluciones Sin Conexión Primero",
          offlineFirstDesc: "Operar sin internet usando servidores locales",
          languagePreservation: "Preservación de Idiomas",
          languagePreservationDesc:
            "Entrenar modelos de IA para lenguas indígenas",
          territoryDefense: "Defensa del Territorio",
          territoryDefenseDesc:
            "Herramientas seguras para documentar información sensible",
          mapeoIntegration: "Integración con Mapeo",
          mapeoIntegrationDesc:
            "Crear y gestionar geo-observaciones fácilmente a través de WhatsApp",
          terrastoriesConnection: "Conexión con Terrastories",
          terrastoriesConnectionDesc:
            "Comparte y preserva las historias de tu comunidad con facilidad",
          earthDefendersToolkit:
            "Kit de Herramientas para Defensores de la Tierra",
          earthDefendersToolkitDesc:
            "Accede a una gran cantidad de recursos y herramientas para la protección del medio ambiente",
          enhanceAccessibility:
            "Mejorar la accesibilidad a través de tecnología de voz primero",
          implementOffline:
            "Implementar soluciones sin conexión lideradas por la comunidad",
          trainAI: "Entrenar modelos de IA para la preservación de idiomas",
          developTools:
            "Desarrollar herramientas robustas de gestión de proyectos",
          supportSustainable:
            "Apoyar la defensa sostenible del territorio y la preservación cultural",
          integrateWhatsApp:
            "Integrar con WhatsApp para fácil acceso y comunicación",
          empoweredCommunities: "Comunidades indígenas empoderadas",
          languageCulturalPreservation: "Preservación lingüística y cultural",
          increasedAccessibility: "Mayor accesibilidad a la tecnología",
          dataSovereignty: "Soberanía de datos para las comunidades",
          effectiveProjectManagement:
            "Capacidades efectivas de gestión de proyectos",
          simplifiedCommunication:
            "Comunicación simplificada a través de la integración con WhatsApp",
          name: "Nombre",
          email: "Correo electrónico",
          message: "Mensaje",
          send: "Enviar",
        },
      },
      pt: {
        translation: {
          // Portuguese translations
          heroTitle: "Capacitar Comunidades Indígenas com IA",
          heroDescription:
            "Aproveitando a tecnologia offline-first para preservar línguas, proteger territórios e garantir a soberania de dados para comunidades na linha de frente da justiça climática.",
          listenToPodcast: "Ouvir o Podcast",
          aboutTitle: "Sobre o Projeto",
          howItWorksTitle: "Como Funciona",
          featuresTitle: "Principais Características",
          projectOverviewTitle: "Visão Geral do Projeto",
          projectObjectives: "Objetivos do Projeto",
          expectedOutcomes: "Resultados Esperados",
          readyToDefend: "Pronto para Defender a Terra?",
          startUsing: "Comece a usar o Earth Defenders Assistant hoje!",
          talkToUs: "Fale conosco",
          getInTouch: "Entre em Contato",
          // Add more translations here
          voiceFirstTech: "Tecnologia Voz-Primeiro",
          voiceFirstDesc: "Interações de voz naturais em línguas indígenas",
          offlineFirst: "Soluções Offline-Primeiro",
          offlineFirstDesc: "Operar sem internet usando servidores locais",
          languagePreservation: "Preservação de Línguas",
          languagePreservationDesc:
            "Treinar modelos de IA para línguas indígenas",
          territoryDefense: "Defesa do Território",
          territoryDefenseDesc:
            "Ferramentas seguras para documentar informações sensíveis",
          mapeoIntegration: "Integração com Mapeo",
          mapeoIntegrationDesc:
            "Crie e gerencie geo-observações facilmente através do WhatsApp",
          terrastoriesConnection: "Conexão com Terrastories",
          terrastoriesConnectionDesc:
            "Compartilhe e preserve as histórias da sua comunidade com facilidade",
          earthDefendersToolkit: "Kit de Ferramentas dos Defensores da Terra",
          earthDefendersToolkitDesc:
            "Acesse uma riqueza de recursos e ferramentas para proteção ambiental",
          enhanceAccessibility:
            "Melhorar a acessibilidade através da tecnologia voz-primeiro",
          implementOffline:
            "Implementar soluções offline-primeiro lideradas pela comunidade",
          trainAI: "Treinar modelos de IA para preservação de línguas",
          developTools:
            "Desenvolver ferramentas robustas de gestão de projetos",
          supportSustainable:
            "Apoiar a defesa sustentável do território e a preservação cultural",
          integrateWhatsApp:
            "Integrar com WhatsApp para fácil acesso e comunicação",
          empoweredCommunities: "Comunidades indígenas empoderadas",
          languageCulturalPreservation: "Preservação linguística e cultural",
          increasedAccessibility: "Maior acessibilidade à tecnologia",
          dataSovereignty: "Soberania de dados para as comunidades",
          effectiveProjectManagement:
            "Capacidades efetivas de gestão de projetos",
          simplifiedCommunication:
            "Comunicação simplificada através da integração com WhatsApp",
          name: "Nome",
          email: "E-mail",
          message: "Mensagem",
          send: "Enviar",
        },
      },
    },
    fallbackLng: "en",
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
