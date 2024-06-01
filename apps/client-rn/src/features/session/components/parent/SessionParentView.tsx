import { useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useEffect, useMemo, useRef } from "react";
import { useTranslation } from "react-i18next";
import { Text, View } from "react-native"
import Animated ,{ ZoomIn } from 'react-native-reanimated';

const ParentGuideView = (props: {
    id: string,
    order: number,
    style?: any
}) => {
    const topicCategory = useSelector(state => state.session.topic.category)
    const guide = useSelector(state => state.session.parentGuideEntityState.entities[props.id])

    const enteringAnim = useMemo(() => ZoomIn.springify().duration(600).delay(props.order * 100), [props.order])
    
    return <Animated.View entering={enteringAnim} style={props.style} className={`bg-topic${topicCategory}-fg w-[70vw] h-[16vh] justify-center px-8 rounded-2xl border-white border-[4px] shadow-lg shadow-slate-800/60`}>
        <Text style={styleTemplates.withSemiboldFont} className="text-2xl text-white text-center">{guide.guide_localized}</Text>
        </Animated.View>
}

export const SessionParentView = () => {
    
    const isProcessing = useSelector(state => state.session.isProcessingRecommendation)
    const parentGuideIds = useSelector(state => state.session.parentGuideEntityState.ids)

    const {t} = useTranslation()
    
    return <View className="flex-1 self-stretch justify-center items-center">
        {
            isProcessing === true ? <Text style={styleTemplates.withExtraboldFont} className="text-lg">{t("Session.LoadingMessage.ParentGuide")}</Text> : <View className="gap-8">
                {parentGuideIds.map((id, i) => <ParentGuideView key={id} id={id} order={i}/>)}
            </View>
        }
    </View>
}