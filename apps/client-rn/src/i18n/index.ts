import { initializeI18n } from "@aacesstalk/libs/ts-core";
import { initReactI18next } from "react-i18next";

initializeI18n("kr", {
    resources: {
        kr: {translation: require('./translations/kr')}
    },
    middlewares: [initReactI18next]
})