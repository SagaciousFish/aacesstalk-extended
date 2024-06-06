import { DialogueRole, cancelSession, endSession } from "@aacesstalk/libs/ts-core";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { PopupMenuItemView } from "apps/client-rn/src/components/PopupMenuItemView";
import { PopupMenuScreenFrame } from "apps/client-rn/src/components/PopupMenuScreenFrame";
import { MainRoutes } from "apps/client-rn/src/navigation";
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks";
import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { Alert } from "react-native";

export const SessionMenuPopupScreen = (props: NativeStackScreenProps<MainRoutes.MainNavigatorParamList, "session-menu">) => {
    
    const {t} = useTranslation()

    const numTurns = useSelector(state => state.session.numTurns)
    const currentTurn = useSelector(state => state.session.currentTurn)

    const pop = useCallback(()=>{
        props.navigation.goBack()
    },[])

    const dispatch = useDispatch()

    const onTerminationPress = useCallback(()=>{

        if(numTurns <= 1){
            console.log("The user did nothing. Just terminate the session without asking.")
            dispatch(cancelSession())
            requestAnimationFrame(props.navigation.popToTop)
        }else{
            Alert.alert(t("Session.Menu.ConfirmTermination"), null, [
                {text: t("Session.Menu.CancelTermination"), style: 'cancel'},
                {text: t("Session.Menu.TerminateAndSave"), style: 'default', onPress: () => {
                    dispatch(endSession())
                    props.navigation.pop()
                    //TODO go to result screen
                }},
            ], {cancelable: true})
        }
    }, [t, numTurns])

    const onNextTurnPress = useCallback(()=>{
        switch(currentTurn){
            case DialogueRole.Parent:
                
                break;
            case DialogueRole.Child:
                break;
        }
    }, [currentTurn])
    
    return <PopupMenuScreenFrame onPop={pop}>
        <PopupMenuItemView title={t("Session.Menu.NextTurn")} onPress={onNextTurnPress}/>
        <PopupMenuItemView title={t("Session.Menu.TerminateSession")} destructive onPress={onTerminationPress}/>
    </PopupMenuScreenFrame>
}