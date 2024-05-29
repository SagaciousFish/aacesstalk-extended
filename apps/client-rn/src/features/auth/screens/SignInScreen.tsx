import { useTranslation } from "react-i18next"
import { View, Text, TextInput } from "react-native"
import LogoImage from '../../../assets/images/logo-extended.svg'
import { styleTemplates } from "apps/client-rn/src/styles"
import { HillBackgroundView } from "apps/client-rn/src/components/HillBackgroundView"
import colors from "tailwindcss/colors"
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components"
import { Control, useController, useForm } from "react-hook-form"
import {yupResolver} from "@hookform/resolvers/yup";
import * as yup from "yup";
import { useMemo } from "react"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { loginDyadThunk } from "@aacesstalk/libs/ts-core"

const PasscodeInput = (props: {
    control: Control,
    name: string,
    onSubmit?: () => void
}) => {

    const {field, fieldState: {error, invalid}} = useController(props)

    const {t} = useTranslation()

    return <TextInput 
    placeholder={t("SignIn.InsertNumber")} 
    placeholderTextColor={colors.slate[400]} 
    style={styleTemplates.withSemiboldFont}
    textAlign="center"
    multiline={true}
    numberOfLines={1}
    className="mt-4 py-3 text-xl text-center bg-white rounded-xl border-[#11111345] border-2 focus:border-teal-500 focus:border-[3px]"
    keyboardType="numeric"
    inputMode="numeric"
    autoCapitalize="none"
    autoComplete="off"
    secureTextEntry={true}

    ref={field.ref}
    value={field.value}
    onChangeText={field.onChange}
    onBlur={field.onBlur}
    onSubmitEditing={props.onSubmit}
    blurOnSubmit={true}
    returnKeyType="go"
    />
}

export const SignInScreen = () => {

    const {t} = useTranslation()

    const isAuthorizing  = useSelector(state => state.auth.isAuthorizing)
    const authorizationError  = useSelector(state => state.auth.error)

    const dispatch = useDispatch()

    const schema = useMemo(()=> yup.object({
        passcode: yup.string().min(1).required()
    }), [])

    const {control, handleSubmit, setFocus, formState: {isValid, errors}, setError} = useForm({
        resolver: yupResolver(schema)
    })

    const onSubmit = useMemo(() => handleSubmit(async (values) => {
            dispatch(loginDyadThunk(values.passcode))
        }), [])

    return <HillBackgroundView containerClassName="items-center justify-center pb-[200px]">
        <View className="items-stretch">
            <LogoImage className="justify-self-center" width={400} height={150}/>
            {
                isAuthorizing === true ? <Text className="text-center text-lg text-slate-500" style={styleTemplates.withBoldFont}>{t("SignIn.Authorizing")}</Text> : <>
                    {
                        authorizationError ? <Text className="text-center text-lg text-red-400 mt-4" style={styleTemplates.withBoldFont}>{t(`SignIn.Errors.${authorizationError}`)}</Text> : null
                    }
                    <PasscodeInput control={control} name="passcode" onSubmit={onSubmit}/>
                    <TailwindButton title={t("SignIn.SignIn")} containerClassName="mt-5" roundedClassName={"rounded-full"} 
                        titleClassName="text-white"
                        rippleColor="#f0f0f080"
                        disabled={!isValid}
                        disabledButtonStyleClassName="bg-[#e0e0e0]"
                        buttonStyleClassName="bg-[#F9AA33]"
                        onPress={onSubmit}
                        />
                </>
            }
            
        </View>
    </HillBackgroundView>
}