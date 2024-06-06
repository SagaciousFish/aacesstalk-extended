import { useMemo } from 'react'
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useTranslation } from "react-i18next";
import { Text, TextInput, View } from "react-native"
import { ParentGuideElementView } from "./ParentGuideElementView";
import { MultiTapButton } from "apps/client-rn/src/components/MultiTapButton";
import { useCallback, useState } from "react";
import { LoadingIndicator } from "apps/client-rn/src/components/LoadingIndicator";
import { PopupMenuScreenFrame } from "apps/client-rn/src/components/PopupMenuScreenFrame";
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components";
import { useController, useForm } from "react-hook-form";
import { submitParentMessage } from '@aacesstalk/libs/ts-core';

const ParentMessageTextInputView = (props: {
    onPopTextInput: () => void,
}) => {

    const { control, handleSubmit, formState: {isValid, errors} } = useForm({defaultValues: {message: ""}})

    const {field} = useController({control, name: "message", rules: {
        required: true, minLength:1
    }})

    const dispatch = useDispatch()

    const onSubmit = useMemo(()=> handleSubmit((values)=>{
        props.onPopTextInput()
        dispatch(submitParentMessage(values.message))
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

export const SessionParentView = () => {
    
    const isProcessing = useSelector(state => state.session.isProcessingRecommendation)
    const parentGuideIds = useSelector(state => state.session.parentGuideEntityState.ids)
    const topic = useSelector(state => state.session.topic)

    const {t} = useTranslation()

    const [isTextInputOn, setIsTextInputOn] = useState(false)    

    const onTapSecretButton = useCallback(()=>{
        console.log("Tapped a secret button.")
        setIsTextInputOn(!isTextInputOn)
    }, [isTextInputOn])

    const onPopTextInput = useCallback(()=>{
        setIsTextInputOn(false)
    },[])
    
    return <>
        <MultiTapButton numberOfTaps={5} onTapGesture={onTapSecretButton}><View className="absolute top-0 left-0 w-20 h-20 bg-transparent"/></MultiTapButton>
        <View className="flex-1 self-stretch justify-center items-center mb-8 mt-5">
        {
            isProcessing === true ? <LoadingIndicator colorTopic={topic?.category} label={t("Session.LoadingMessage.ParentGuide")}/> : <View className="justify-evenly flex-1">
                {parentGuideIds.map((id, i) => <ParentGuideElementView key={id} id={id} order={i}/>)}
            </View>
        }
        </View>
        {
            isTextInputOn ? <ParentMessageTextInputView onPopTextInput={onPopTextInput}/> : null
        }
    </>
}