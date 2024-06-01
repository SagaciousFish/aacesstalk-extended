import { StyleSheet } from 'react-native'
import { TopicCategory } from '@aacesstalk/libs/ts-core'
import { NativeStackScreenProps } from '@react-navigation/native-stack'
import { MainRoutes } from 'apps/client-rn/src/navigation'
import { View, Text } from 'react-native'
import HillPlanImage from '../../../assets/images/hill_plan.svg'
import HillRecallImage from '../../../assets/images/hill_recall.svg'
import HillFreeImage from '../../../assets/images/hill_free.svg'
import { HillBackgroundView } from 'apps/client-rn/src/components/HillBackgroundView'
import { SessionTitleRibbon } from '../components/SessionTitleRibbon'
import { useTranslation } from 'react-i18next'
import { useSelector } from 'apps/client-rn/src/redux/hooks'
import { Fragment, useMemo } from 'react'
import format from 'string-template'
import { SessionStartingMessage } from '../components/SessionStartingMessage'

const BG_COLOR_BY_TOPIC_CATEGORY = {
    [TopicCategory.Plan]: 'bg-topicplan-bg',
    [TopicCategory.Recall]: 'bg-topicrecall-bg',
    [TopicCategory.Free]: 'bg-topicfree-bg',
}

const styles = StyleSheet.create({
    hill: {
        zIndex: -1,
        position: 'absolute',
        bottom: 0
    }
})

export const SessionScreen = (props: NativeStackScreenProps<MainRoutes.MainNavigatorParamList, "session">) => {

    const {t} = useTranslation()

    let HillView
    switch(props.route.params.topic.category){
        case TopicCategory.Plan:
            HillView = HillPlanImage
            break;
        case TopicCategory.Recall:
            HillView = HillRecallImage
            break;
        case TopicCategory.Free:
            HillView = HillFreeImage
            break;
        default:
            throw Error("Unsupported topic category.")
    }

    return <HillBackgroundView containerClassName={`items-center ${BG_COLOR_BY_TOPIC_CATEGORY[props.route.params.topic.category]}`} hillComponentClass={HillView} hillImageHeight={165}>
        <SessionTitleRibbon containerClassName="mt-12" topic={props.route.params.topic}/>
        <Fragment key={"session-content"}>
            <SessionStartingMessage topic={props.route.params.topic} containerClassName='mt-14'/>
        </Fragment>
    </HillBackgroundView>
}