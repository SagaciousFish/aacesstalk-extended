import { useTranslation } from "react-i18next"
import { View, Text } from "react-native"
import LogoImage from '../../../assets/images/logo-extended.svg'
import { styleTemplates } from "apps/client-rn/src/styles"
import { HillBackgroundView } from "apps/client-rn/src/components/HillBackgroundView"
import { Button, Input } from "@rneui/themed"

export const SignInScreen = () => {

    const {t} = useTranslation()

    return <HillBackgroundView containerClassName="items-center justify-center pb-[120px]">
        <View className="items-stretch">
            <LogoImage className="justify-self-center" width={400} height={150}/>
            <Button title={t("SignIn.SignIn")}/>
        </View>
    </HillBackgroundView>
}