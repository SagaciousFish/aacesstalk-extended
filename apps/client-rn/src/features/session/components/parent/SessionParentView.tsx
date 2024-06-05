import { useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useTranslation } from "react-i18next";
import { Text, View } from "react-native"
import { ParentGuideElementView } from "./ParentGuideElementView";
import { MultiTapButton } from "apps/client-rn/src/components/MultiTapButton";
import { useCallback, useState } from "react";
import { LoadingIndicator } from "apps/client-rn/src/components/LoadingIndicator";


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
    
    return <>
        <MultiTapButton numberOfTaps={5} onTapGesture={onTapSecretButton}><View className="absolute top-0 left-0 w-20 h-20 bg-transparent"/></MultiTapButton>
        <View className="flex-1 self-stretch justify-center items-center mb-8 mt-5">
        {
            isProcessing === true ? <LoadingIndicator colorTopic={topic?.category} label={t("Session.LoadingMessage.ParentGuide")}/> : <View className="justify-evenly flex-1">
                {parentGuideIds.map((id, i) => <ParentGuideElementView key={id} id={id} order={i}/>)}
            </View>
        }
        </View>
    </>
}