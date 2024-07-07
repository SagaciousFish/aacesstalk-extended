import { SessionTopicInfo, TopicCategory } from "@aacesstalk/libs/ts-core"
import { useSelector } from "apps/client-rn/src/redux/hooks"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import format from "pupa"
import {Text} from "react-native"
import { styleTemplates } from "apps/client-rn/src/styles"

export const SessionStartingMessage = (props: {
    topic: SessionTopicInfo,
    containerClassName?: string
}) => {
    
    const {t} = useTranslation()

    const child_name = useSelector(state => state.auth.dyadInfo?.child_name)
    
    const message = useMemo(()=>{
        switch(props.topic.category){
            case TopicCategory.Plan:
                return format(t("Session.StartingMessage.PlanTemplate"), {child_name})
            case TopicCategory.Recall:
                return format(t("Session.StartingMessage.RecallTemplate"), {child_name})
            case TopicCategory.Free:
                return format(t("Session.StartingMessage.FreeTemplate"), {child_name})
        }
    }, [t, child_name, props.topic.category])

    return <Text style={styleTemplates.withBoldFont} className={`text-3xl text-slate-700 ${props.containerClassName}`}>
        {message}
    </Text>
}