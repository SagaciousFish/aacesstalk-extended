import { useTranslation } from "react-i18next"
import { View, Text, Pressable, TextInput } from "react-native"
import LogoImage from '../../../assets/images/logo-extended.svg'
import { styleTemplates } from "apps/client-rn/src/styles"
import { HillBackgroundView } from "apps/client-rn/src/components/HillBackgroundView"
import colors from "tailwindcss/colors"
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components"

export const SignInScreen = () => {

    const {t} = useTranslation()

    return <HillBackgroundView containerClassName="items-center justify-center pb-[200px]">
        <View className="items-stretch">
            <LogoImage className="justify-self-center" width={400} height={150}/>
            <TextInput 
                placeholder={t("SignIn.InsertNumber")} 
                placeholderTextColor={colors.slate[400]} 
                style={styleTemplates.withSemiboldFont} 
                className="mt-4 py-3 text-xl text-center bg-white rounded-xl border-[#11111345] border-2 focus:border-teal-500 focus:border-[3px]"
                keyboardType="numeric"
                inputMode="numeric"
                />
            <TailwindButton title={t("SignIn.SignIn")} containerClassName="mt-5" roundedClassName={"rounded-full"} 
                titleClassName="text-white"
                rippleColor="#f0f0f080"
                disabled={true}
                disabledButtonStyleClassName="bg-[#e0e0e0]"
                buttonStyleClassName="bg-[#F9AA33]"/>
        </View>
    </HillBackgroundView>
}