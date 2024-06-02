import { useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useTranslation } from "react-i18next";
import { Text, View } from "react-native"
import { ParentGuideElementView } from "./ParengGuideElementView";


export const SessionParentView = () => {
    
    const isProcessing = useSelector(state => state.session.isProcessingRecommendation)
    const parentGuideIds = useSelector(state => state.session.parentGuideEntityState.ids)

    const {t} = useTranslation()
    
    return <View className="flex-1 self-stretch justify-center items-center mb-8 mt-5">
        {
            isProcessing === true ? <Text style={styleTemplates.withExtraboldFont} className="text-lg">{t("Session.LoadingMessage.ParentGuide")}</Text> : <View className="justify-evenly flex-1">
                {parentGuideIds.map((id, i) => <ParentGuideElementView key={id} id={id} order={i}/>)}
            </View>
        }
    </View>
}