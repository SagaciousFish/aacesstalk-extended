import { DialogueRole, cancelSession, confirmSelectedCards, endSession, isChildCardConfirmValidSelector } from "@aacesstalk/libs/ts-core";
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

    const sessionId = useSelector(state => state.session.id)
    const numTurns = useSelector(state => state.session.numTurns)
    const currentTurn = useSelector(state => state.session.currentTurn)

    const canSubmitSelectedChildCards = useSelector(isChildCardConfirmValidSelector)

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
                    props.navigation.replace(MainRoutes.ROUTE_SESSION_CLOSING, { sessionId })
                }},
            ], {cancelable: true})
        }
    }, [t, numTurns, sessionId])

    const onNextTurnPress = useCallback(()=>{
        switch(currentTurn){
            case DialogueRole.Parent:
                //TODO submit parent message
                break;
            case DialogueRole.Child:
                if(canSubmitSelectedChildCards === true){    
                    dispatch(confirmSelectedCards())
                    props.navigation.pop()
                }
                break;
        }
    }, [currentTurn])
    
    return <PopupMenuScreenFrame onPop={pop}>
        <PopupMenuItemView title={t("Session.Menu.NextTurn")} onPress={onNextTurnPress} disabled={!canSubmitSelectedChildCards}/>
        <PopupMenuItemView title={t("Session.Menu.TerminateSession")} destructive onPress={onTerminationPress}/>
    </PopupMenuScreenFrame>
}