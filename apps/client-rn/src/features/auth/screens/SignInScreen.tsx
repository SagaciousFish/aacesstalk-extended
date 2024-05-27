import { useTranslation } from "react-i18next"
import { View, Text } from "react-native"

export const SignInScreen = () => {

    const {t} = useTranslation()

    return <View>
        <Text>{t("SignIn.InsertNumber")}</Text>
    </View>
}