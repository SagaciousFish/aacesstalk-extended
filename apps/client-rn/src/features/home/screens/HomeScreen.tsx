import { HillBackgroundView } from "apps/client-rn/src/components/HillBackgroundView"
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useTranslation } from "react-i18next"
import { Text, View } from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"

export const HomeScreen = () => {

    const {t} = useTranslation()

    return <HillBackgroundView containerClassName="items-center justify-center">
        <SafeAreaView className="flex-1 self-stretch items-center justify-center">
            <Text className="text-3xl text-slate-800 text-center" style={styleTemplates.withBoldFont}>{t("TopicSelection.Title")}</Text>
            <TailwindButton containerClassName="absolute right-5 bottom-5" buttonStyleClassName="py-5 px-12" roundedClassName="rounded-full" title={t("TopicSelection.StarCount")}></TailwindButton>
        </SafeAreaView>
        </HillBackgroundView>
}