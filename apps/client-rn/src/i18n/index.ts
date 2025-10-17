import { initializeI18n } from "@aacesstalk/libs/ts-core";
import { initReactI18next } from "react-i18next";

initializeI18n("cn", {
    resources: {
        cn: {translation: require('./translations/cn')},
        en: {translation: require('./translations/en')},
        kr: {translation: require('./translations/kr')},
    },
    middlewares: [initReactI18next]
})