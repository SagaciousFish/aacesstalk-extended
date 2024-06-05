import { DialogueRole, TopicCategory, requestParentGuides } from '@aacesstalk/libs/ts-core'
import { NativeStackScreenProps } from '@react-navigation/native-stack'
import { MainRoutes } from 'apps/client-rn/src/navigation'
import HillPlanImage from '../../../assets/images/hill_plan.svg'
import HillRecallImage from '../../../assets/images/hill_recall.svg'
import HillFreeImage from '../../../assets/images/hill_free.svg'
import { HillBackgroundView } from 'apps/client-rn/src/components/HillBackgroundView'
import { SessionTitleRibbon } from '../components/SessionTitleRibbon'
import { useTranslation } from 'react-i18next'
import { useDispatch, useSelector } from 'apps/client-rn/src/redux/hooks'
import { Fragment, useCallback, useEffect } from 'react'
import { SessionStartingMessage } from '../components/SessionStartingMessage'
import { SessionParentView } from '../components/parent/SessionParentView'
import { TailwindButton } from 'apps/client-rn/src/components/tailwind-components'
import { MenuIcon } from 'apps/client-rn/src/components/vector-icons'
import Animated, { Easing, SlideInDown } from 'react-native-reanimated'
import { SessionChildView } from '../components/child/SessionChildView'

const BG_COLOR_BY_TOPIC_CATEGORY = {
    [TopicCategory.Plan]: 'bg-topicplan-bg',
    [TopicCategory.Recall]: 'bg-topicrecall-bg',
    [TopicCategory.Free]: 'bg-topicfree-bg',
}

const menuButtonEnteringAnim = SlideInDown.duration(500).delay(300).easing(Easing.elastic(0.7))

export const SessionScreen = (props: NativeStackScreenProps<MainRoutes.MainNavigatorParamList, "session">) => {

    const {t} = useTranslation()

    const dispatch = useDispatch()

    const isInitializing = useSelector(state => state.session.isInitializing)
    const sessionId = useSelector(state => state.session.id)

    const currentTurn = useSelector(state => state.session.currentTurn)

    useEffect(()=>{
        console.log(isInitializing)
        if(isInitializing == false && sessionId != null){
            dispatch(requestParentGuides())
        }
    }, [isInitializing, sessionId])

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

    const onMenuButtonPress = useCallback(()=>{
        props.navigation.navigate('session-menu')
    }, [])

    return <HillBackgroundView containerClassName={`items-center ${BG_COLOR_BY_TOPIC_CATEGORY[props.route.params.topic.category]}`} hillComponentClass={HillView} hillImageHeight={165}>
        <SessionTitleRibbon containerClassName="mt-12" topic={props.route.params.topic}/>
        <Fragment key={"session-content"}>
            <SessionStartingMessage topic={props.route.params.topic} containerClassName='mt-14'/>
            {
                currentTurn === DialogueRole.Parent? <SessionParentView/> : <SessionChildView/>
            }
        </Fragment>
        <Animated.View className='absolute left-5 bottom-5' entering={menuButtonEnteringAnim}>
            <TailwindButton onPress={onMenuButtonPress} roundedClassName='rounded-xl' buttonStyleClassName='p-3'><MenuIcon width={32} height={32} fill={"#575757"}/></TailwindButton>        
        </Animated.View>
    </HillBackgroundView>
}