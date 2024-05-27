import i18next, { i18n } from "i18next";

export function initializeI18n(defaultLanguage: string = "kr", middlewares?: Array<any>) {
    let i18nInstance = i18next

    if(middlewares != null && middlewares.length > 0){
        for(const middleware of middlewares){
            i18nInstance = i18nInstance.use(middleware)
        }
    }

    i18nInstance.init({
        fallbackLng: 'kr',
        lng: defaultLanguage,
        resources: {
            kr: {
                translation: require("./translations/kr")
            }
        },
        react: {
            useSuspense: true
        },
        debug: false
    }, (err, t) => {
        if (err) {
            console.log("Error on initializing i18n - ", err)
        } else {
            console.log("Successfully initialized i18n module.")
        }
    })
}