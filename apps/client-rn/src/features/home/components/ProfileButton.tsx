import { signOutDyadThunk } from "@aacesstalk/libs/ts-core"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useCallback, useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Alert, View, Text } from "react-native"
import { Gesture, GestureDetector } from "react-native-gesture-handler"
import format from "string-template"

export const ProfileButton = () => {
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