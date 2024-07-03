import { useCallback, useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "../../redux/hooks";
import { AACessTalkErrors, DialogueRole, confirmSelectedCards, isChildCardConfirmValidSelector, isInteractionEnabledSelector } from "@aacesstalk/libs/ts-core";
import { stopRecording } from "../audio/reducer";
import Toast from "react-native-toast-message";
import { useTranslation } from "react-i18next";
import KeyEvent from 'react-native-global-keyevent';
import { usePrevious } from "../../utils/hooks";

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
                    dispatch(confirmSelectedCards())
                    onGoNext?.(currentTurn)
                }else{
                    onGoNextFail?.(currentTurn)
                }
                break;
        }
    }, [currentTurn, t])
}

export function useEnterKeyEvent(listening: boolean=true, onKeyPress?: ()=>boolean) {

    const isInteractionEnabled = useSelector(isInteractionEnabledSelector)
    
    const isKeyInputConsumed = useRef(false)

    useEffect(()=>{
        isKeyInputConsumed.current = false
    }, [isInteractionEnabled])

    useEffect(()=>{
        /*
        const downListener = KeyEvent.addKeyDownListener((event) => {
            if(event.keyCode == 66 && listening == true && isInteractionEnabled){
            }
        })*/
        
        const upListener = KeyEvent.addKeyUpListener((event) => {
            if(event.keyCode == 66 && listening == true && isInteractionEnabled){
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