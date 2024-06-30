import { useEffect, useMemo } from 'react'
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useTranslation } from "react-i18next";
import { InteractionManager, TextInput, View } from "react-native"
import { ParentGuideElementView } from "./ParentGuideElementView";
import { MultiTapButton } from "apps/client-rn/src/components/MultiTapButton";
import { useCallback, useState } from "react";
import { LoadingIndicator } from "apps/client-rn/src/components/LoadingIndicator";
import { PopupMenuScreenFrame } from "apps/client-rn/src/components/PopupMenuScreenFrame";
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components";
import { useController, useForm } from "react-hook-form";
import { SessionTopicInfo, parentGuideSelectors, submitParentMessageText } from '@aacesstalk/libs/ts-core';
import { SessionTitleRibbon } from '../SessionTitleRibbon';
import { SessionStartingMessage } from './SessionStartingMessage';
import { useNonNullUpdatedValue } from 'apps/client-rn/src/utils/hooks';
import { TurnStar } from '../TurnStar';
import { pauseRecording, resumeRecording } from '../../../audio/reducer';
import { RecordingIndicator } from './RecordingIndicator';

const ParentMessageTextInputView = (props: {
    onPopTextInput: () => void,
}) => {

    const { control, handleSubmit, formState: {isValid, errors} } = useForm({defaultValues: {message: ""}})

    const {field} = useController({control, name: "message", rules: {
        required: true, minLength:1
    }})

    const dispatch = useDispatch()

    const onSubmit = useMemo(()=> handleSubmit((values)=>{
        InteractionManager.runAfterInteractions(()=>{
            props.onPopTextInput()
            dispatch(submitParentMessageText(values.message))
        })
    }), [])

    return <PopupMenuScreenFrame onPop={props.onPopTextInput} 
    backgroundClassName="absolute left-0 right-0 top-0 bottom-0" panelClassName="w-[80vw]">
        <View className="flex-row p-3">
            <TextInput 
                ref={field.ref}
                value={field.value}
                onChangeText={field.onChange}
                onBlur={field.onBlur}
                onSubmitEditing={onSubmit}
                blurOnSubmit={true}
                returnKeyType="go"
                className="flex-1 mr-3 bg-slate-200 rounded-lg text-lg p-2 px-4" placeholder="Enter parent message." style={styleTemplates.withBoldFont}/>
            <TailwindButton disabled={!isValid} title="Submit" buttonStyleClassName="bg-teal-500" disabledButtonStyleClassName="bg-teal-500/50" titleClassName="text-white" roundedClassName="rounded-lg" onPress={onSubmit}/>
        </View>
    </PopupMenuScreenFrame>
}

export const SessionParentView = (props: {
    topic: SessionTopicInfo
}) => {
    const dispatch = useDispatch()
    
    const isProcessing = useSelector(state => state.session.isProcessingRecommendation)
    const parentGuideIds = useSelector(parentGuideSelectors.selectIds)

    const numTurns = useSelector(state => state.session.numTurns)

    const numStarsLoopArray = useMemo(()=>{
        return new Array(Math.floor(numTurns/2)).fill(null)
    }, [numTurns])

    const {t} = useTranslation()

    const [isTextInputOn, setIsTextInputOn] = useState(false)    

    const onTapSecretButton = useCallback(()=>{
        console.log("Tapped a secret button.")
        setIsTextInputOn(!isTextInputOn)
    }, [isTextInputOn])

    const onPopTextInput = useCallback(()=>{
        setIsTextInputOn(false)
    },[])

    useEffect(()=>{
        if(isTextInputOn === true){
            dispatch(pauseRecording())
        }else{
            dispatch(resumeRecording())
        }
    }, [isTextInputOn])

    const topic = useNonNullUpdatedValue(props.topic)
    
    return <>
        <SessionTitleRibbon containerClassName="mt-12" topic={topic} />
        <RecordingIndicator/>
        {
            numTurns == 0 ? <SessionStartingMessage topic={topic} containerClassName='mt-14' /> : <View pointerEvents='none' className='mt-12 flex-row space-x-3'>
                {
                    numStarsLoopArray.map((_, index) => {
                        if(index < numStarsLoopArray.length - 1){
                            return <TurnStar key={index} useEnteringAttentionAnimation={false}/>
                        }else{
                            return null
                        }
                    })
                }
                {
                    numStarsLoopArray.length > 0 ? <TurnStar useEnteringAttentionAnimation/> : null // Animate only last star.
                }
            </View>
        }
        <MultiTapButton numberOfTaps={5} onTapGesture={onTapSecretButton}><View className="absolute top-0 left-0 w-20 h-20 bg-transparent"/></MultiTapButton>
        <View className="flex-1 self-stretch justify-center items-center mb-8 mt-5">
        {
            isProcessing === true ? <LoadingIndicator colorTopic={topic.category} label={t("Session.LoadingMessage.ParentGuide")}/> : <View className="justify-evenly flex-1">
                {parentGuideIds.map((id, i) => <ParentGuideElementView key={id} id={id} order={i}/>)}
            </View>
        }
        </View>
        {
            isTextInputOn ? <ParentMessageTextInputView onPopTextInput={onPopTextInput}/> : null
        }
    </>
}