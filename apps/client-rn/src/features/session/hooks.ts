import { useCallback, useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "../../redux/hooks";
import { AACessTalkErrors, DialogueRole, confirmSelectedCards, isChildCardConfirmValidSelector, isInteractionEnabledSelector } from "@aacesstalk/libs/ts-core";
import { stopRecording } from "../audio/reducer";
import Toast from "react-native-toast-message";
import { useTranslation } from "react-i18next";
import KeyEvent from 'react-native-global-keyevent';

export function useMoveNextTurn(
    onGoNext?: (currentTurn: DialogueRole) => void,
    onGoNextFail?: (currentTurn: DialogueRole) => void
): () => void {

    const dispatch = useDispatch()
    
    const currentTurn = useSelector(state => state.session.currentTurn)

    const canSubmitSelectedChildCards = useSelector(isChildCardConfirmValidSelector)

    const {t} = useTranslation()

    return useCallback(()=>{
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
                onGoNext?.(currentTurn)
                break;
            case DialogueRole.Child:
                if(canSubmitSelectedChildCards === true){  
                    Toast.hide()  
                    dispatch(confirmSelectedCards())
                    onGoNext?.(currentTurn)
                }else{
                    Toast.show({
                        type: 'warning',
                        position: 'bottom',
                        bottomOffset: 100,
                        visibilityTime: 6000,
                        text1: "카드를 선택해야 다음으로 넘어갈 수 있어요!"
                    })
                    onGoNextFail?.(currentTurn)
                }
                break;
        }
    }, [currentTurn, t, canSubmitSelectedChildCards])
}

export function useEnterKeyEvent(listening: boolean=true, onKeyPress?: ()=>boolean) {

    const isInteractionEnabled = useSelector(isInteractionEnabledSelector)
    
    const isKeyInputConsumed = useRef(false)

    useEffect(()=>{
        if(isInteractionEnabled === true){
            isKeyInputConsumed.current = false
        }
    }, [isInteractionEnabled])

    useEffect(()=>{
        /*
        const downListener = KeyEvent.addKeyDownListener((event) => {
            if(event.keyCode == 66 && listening == true && isInteractionEnabled){
            }
        })*/
        
        const upListener = KeyEvent.addKeyUpListener((event) => {
            console.log("Key up event - ", listening, isInteractionEnabled, isKeyInputConsumed.current)
            //66 : enter, 160: numpad enter. Support third-party enter buttons
            if((event.keyCode == 66 || event.keyCode == 160 ) && listening == true && isInteractionEnabled){
                if(isKeyInputConsumed.current == false){
                    isKeyInputConsumed.current = onKeyPress?.() || false
                }
            }
        })

        return () => {
            //downListener.remove()
            upListener.remove()
        }
    }, [onKeyPress, isInteractionEnabled, listening])


}