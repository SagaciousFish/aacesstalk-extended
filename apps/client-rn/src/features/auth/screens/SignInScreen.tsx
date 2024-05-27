import { useTranslation } from "react-i18next"
import { View, Text } from "react-native"
import LogoImage from '../../../assets/images/logo-extended.svg'
import { styleTemplates } from "apps/client-rn/src/styles"
import { HillBackgroundView } from "apps/client-rn/src/components/HillBackgroundView"

export const SignInScreen = () => {

    const {t} = useTranslation()

    return <HillBackgroundView containerClassName="items-center justify-center pb-[120px]">
        <View className="items-stretch">
            <LogoImage className="justify-self-center" width={400} height={150}/>
            <Text style={styleTemplates.withSemiboldFont} className="text-xl bg-red-500 text-center mt-8">{t("SignIn.InsertNumber")}</Text>
        </View>
    </HillBackgroundView>
}