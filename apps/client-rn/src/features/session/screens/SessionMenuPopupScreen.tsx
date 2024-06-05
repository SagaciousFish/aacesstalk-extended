import { cancelSession, endSession } from "@aacesstalk/libs/ts-core";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { PopupMenuItemView } from "apps/client-rn/src/components/PopupMenuItemView";
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components";
import { ExIcon } from "apps/client-rn/src/components/vector-icons";
import { MainRoutes } from "apps/client-rn/src/navigation";
import { useDispatch } from "apps/client-rn/src/redux/hooks";
import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { View, Text, Pressable, Alert } from "react-native";
import Reanimated, { Easing, SlideInDown, SlideInRight, SlideInUp, SlideOutDown } from 'react-native-reanimated';
import { useTransitionProgress } from "react-native-screens";

export const SessionMenuPopupScreen = (props: NativeStackScreenProps<MainRoutes.MainNavigatorParamList, "session-menu">) => {
    
    const {t} = useTranslation()

    const pop = useCallback(()=>{
        props.navigation.goBack()
    },[])

    const dispatch = useDispatch()

    const onTerminationPress = useCallback(()=>{
        Alert.alert(t("Session.Menu.ConfirmTermination"), null, [
            {text: t("Session.Menu.CancelTermination"), style: 'cancel'},
            {text: t("Session.Menu.TerminateWithoutSave"), style: 'destructive', onPress: () => {
                dispatch(cancelSession())
                requestAnimationFrame(props.navigation.popToTop)
                
            }},
            {text: t("Session.Menu.TerminateAndSave"), style: 'default', onPress: () => {
                dispatch(endSession())
                //TODO go to result screen
            }},
        ], {cancelable: true})
    }, [t, dispatch])

    const onNextTurnPress = useCallback(()=>{

    }, [])
    
    return <View className="relative flex-1 items-center justify-end bg-slate-800/30">
        <Pressable className="absolute left-0 right-0 top-0 bottom-0" onPress={pop}/>
        <Reanimated.View entering={SlideInDown.duration(400).easing(Easing.out(Easing.cubic))}
            id={"frame"} className="bg-white max-w-[50vw] min-w-[30vw] px-1 pt-1 rounded-t-2xl">
            <TailwindButton onPress={pop} containerClassName="self-end mb-1" buttonStyleClassName="p-2" roundedClassName="rounded-full" shadowClassName="shadow-none"><ExIcon width={32} height={32} fill={"#575757"}/></TailwindButton>
            <PopupMenuItemView title={t("Session.Menu.NextTurn")} onPress={onNextTurnPress}/>
            <PopupMenuItemView title={t("Session.Menu.TerminateSession")} destructive onPress={onTerminationPress}/>
        </Reanimated.View>
        </View>
}