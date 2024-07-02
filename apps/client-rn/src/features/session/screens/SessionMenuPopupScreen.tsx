import { AACessTalkErrors, DialogueRole, cancelSession, confirmSelectedCards, endSession, isChildCardConfirmValidSelector } from "@aacesstalk/libs/ts-core";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { PopupMenuItemView } from "apps/client-rn/src/components/PopupMenuItemView";
import { PopupMenuScreenFrame } from "apps/client-rn/src/components/PopupMenuScreenFrame";
import { MainRoutes } from "apps/client-rn/src/navigation";
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks";
import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { Alert } from "react-native";
import { stopRecording } from "../../audio/reducer";
import Toast from "react-native-toast-message";

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
                    props.navigation.replace(MainRoutes.ROUTE_SESSION_CLOSING, { sessionId, numStars: Math.floor(numTurns/2) })
                }},
            ], {cancelable: true})
        }
    }, [t, numTurns, sessionId])

    const onNextTurnPress = useCallback(()=>{
        switch(currentTurn){
            case DialogueRole.Parent:
                dispatch(stopRecording(false, err => {
                    if(err == AACessTalkErrors.EmptyDictation){
                        Toast.show({
                            type: 'warning',
                            text1: t("ERRORS.EMPTY_DICTATION"),
                            topOffset: 60,
                            visibilityTime: 6000                             
                        })
                    }else{
                        Toast.show({
                            type: 'warning',
                            text1: t("ERRORS.SPEECH_ERROR_GENERAL"),
                            topOffset: 60,
                            visibilityTime: 6000
                        })
                    }
                }))
                props.navigation.pop()
                break;
            case DialogueRole.Child:
                if(canSubmitSelectedChildCards === true){    
                    dispatch(confirmSelectedCards())
                    props.navigation.pop()
                }
                break;
        }
    }, [currentTurn, t])
    
    return <PopupMenuScreenFrame onPop={pop}>
        <PopupMenuItemView title={t("Session.Menu.NextTurn")} onPress={onNextTurnPress} disabled={!((currentTurn == DialogueRole.Child && canSubmitSelectedChildCards) || currentTurn == DialogueRole.Parent)}/>
        <PopupMenuItemView title={t("Session.Menu.TerminateSession")} destructive onPress={onTerminationPress}/>
    </PopupMenuScreenFrame>
}