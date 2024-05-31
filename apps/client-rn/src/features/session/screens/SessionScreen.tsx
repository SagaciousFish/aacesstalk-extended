import { StyleSheet } from 'react-native'
import { TopicCategory } from '@aacesstalk/libs/ts-core'
import { NativeStackScreenProps } from '@react-navigation/native-stack'
import { MainRoutes } from 'apps/client-rn/src/navigation'
import { View, Text } from 'react-native'
import HillPlanImage from '../../../assets/images/hill_plan.svg'
import HillRecallImage from '../../../assets/images/hill_recall.svg'
import HillFreeImage from '../../../assets/images/hill_free.svg'
import { HillBackgroundView } from 'apps/client-rn/src/components/HillBackgroundView'

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

    return <HillBackgroundView containerClassName={`${BG_COLOR_BY_TOPIC_CATEGORY[props.route.params.topic.category]}`} hillComponentClass={HillView} hillImageHeight={165}>
    </HillBackgroundView>
}