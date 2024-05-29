import { signOutDyadThunk } from "@aacesstalk/libs/ts-core"
import { HillBackgroundView } from "apps/client-rn/src/components/HillBackgroundView"
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useCallback, useEffect, useMemo, useRef } from "react"
import { useTranslation } from "react-i18next"
import { Alert, Text, View } from "react-native"
import { Gesture, GestureDetector, TapGesture } from "react-native-gesture-handler"
import { SafeAreaView } from "react-native-safe-area-context"
import format from 'string-template';

const ProfileButton = () => {
    const {child_name, parent_type} = useSelector(state => state.auth.dyadInfo)

    const {t} = useTranslation()

    const dispatch = useDispatch()

    const label = useMemo(()=>{
        return format(t("DyadInfo.FamilyLabelTemplate"), {child_name, parent_type: t(`DyadInfo.ParentType.${parent_type}`)})
    }, [t])

    const onTripplePress = useCallback(()=>{
        Alert.alert(t("SignIn.ConfirmSignOut"), null, [{text: t("SignIn.Cancel"), style: 'cancel'}, {text: t("SignIn.SignOut"), onPress: () => {
            dispatch(signOutDyadThunk())
        }, style: 'destructive'}], {cancelable: true})
    }, [t, dispatch])

    const tripleTap = Gesture.Tap().maxDuration(600).numberOfTaps(3)
    .onStart(onTripplePress) 
    
    return <GestureDetector gesture={tripleTap}><View className="absolute right-5 top-5">
            <Text className={`text-lg text-center text-slate-400`} style={styleTemplates.withSemiboldFont}>{label}</Text>
        </View></GestureDetector>
}

export const HomeScreen = () => {

    const {t} = useTranslation()

    return <HillBackgroundView containerClassName="items-center justify-center">
        <SafeAreaView className="flex-1 self-stretch items-center justify-center">
            <Text className="text-3xl text-slate-800 text-center" style={styleTemplates.withBoldFont}>{t("TopicSelection.Title")}</Text>
            <ProfileButton/>
            <TailwindButton containerClassName="absolute right-5 bottom-5" buttonStyleClassName="py-5 px-12" roundedClassName="rounded-full" title={t("TopicSelection.StarCount")}></TailwindButton>
        </SafeAreaView>
        </HillBackgroundView>
}