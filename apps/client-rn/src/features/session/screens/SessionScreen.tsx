import { DialogueRole, TopicCategory, startAndRetrieveInitialParentGuide } from '@aacesstalk/libs/ts-core'
import { NativeStackScreenProps } from '@react-navigation/native-stack'
import { MainRoutes } from 'apps/client-rn/src/navigation'
import HillPlanImage from '../../../assets/images/hill_plan.svg'
import HillRecallImage from '../../../assets/images/hill_recall.svg'
import HillFreeImage from '../../../assets/images/hill_free.svg'
import { HillBackgroundView } from 'apps/client-rn/src/components/HillBackgroundView'
import { useTranslation } from 'react-i18next'
import { useDispatch, useSelector } from 'apps/client-rn/src/redux/hooks'
import { Fragment, useCallback, useEffect } from 'react'
import { SessionParentView } from '../components/parent/SessionParentView'
import { TailwindButton } from 'apps/client-rn/src/components/tailwind-components'
import { MenuIcon } from 'apps/client-rn/src/components/vector-icons'
import Animated, { Easing, SlideInDown } from 'react-native-reanimated'
import { LoadingIndicator } from 'apps/client-rn/src/components/LoadingIndicator'
import { SessionChildView } from '../components/child/SessionChildView'
import { TailwindClasses } from 'apps/client-rn/src/styles'
import { useDisableBack, usePrevious } from 'apps/client-rn/src/utils/hooks'
import { startRecording, stopRecording } from '../../audio/reducer'
import { InteractionManager } from 'react-native'

const BG_COLOR_BY_TOPIC_CATEGORY = {
    [TopicCategory.Plan]: 'bg-topicplan-bg',
    [TopicCategory.Recall]: 'bg-topicrecall-bg',
    [TopicCategory.Free]: 'bg-topicfree-bg',
}

const menuButtonEnteringAnim = SlideInDown.duration(500).delay(300).easing(Easing.elastic(0.7))

export const SessionScreen = (props: NativeStackScreenProps<MainRoutes.MainNavigatorParamList, "session">) => {

    const { t } = useTranslation()

    useDisableBack()

    const dispatch = useDispatch()

    const isInitializing = useSelector(state => state.session.isInitializing)
    const isLoadingRecommendation = useSelector(state => state.session.isProcessingRecommendation)
    const sessionId = useSelector(state => state.session.id)

    const currentTurn = useSelector(state => state.session.currentTurn)
    const pTurn = usePrevious(currentTurn)

    useEffect(()=>{
        if(pTurn != currentTurn && sessionId != null && currentTurn == DialogueRole.Parent){
            console.log("ParentTurn started.")
            InteractionManager.runAfterInteractions(()=>{
                dispatch(startRecording())
            })
        }

        return () => {
            if(pTurn != currentTurn && sessionId != null && currentTurn == DialogueRole.Parent){
                console.log("Parent turn finished.")
            }
        }
    }, [currentTurn, pTurn, sessionId])

    useEffect(() => {
        if (isInitializing == false && sessionId != null) {
            dispatch(startAndRetrieveInitialParentGuide())
        }
    }, [isInitializing, sessionId])

    useEffect(()=>{
        return () => {
            dispatch(stopRecording(true))
        }
    }, [])

    let HillView
    switch (props.route.params.topic.category) {
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

    const onMenuButtonPress = useCallback(() => {
        props.navigation.navigate('session-menu')
    }, [])

    return <HillBackgroundView containerClassName={`items-center ${BG_COLOR_BY_TOPIC_CATEGORY[props.route.params.topic.category]}`} hillComponentClass={HillView} hillImageHeight={165}>
        {
            isInitializing === true ? <LoadingIndicator colorTopic={props.route.params.topic.category} label={t("Session.LoadingMessage.Initializing")} containerClassName='absolute justify-center self-center left-0 right-0 top-0 bottom-0'/> : null
        }
        <Fragment key={"session-content"}>
            {
                currentTurn === DialogueRole.Parent ? <SessionParentView topic={props.route.params.topic}/> : <SessionChildView/>
            }
        </Fragment>
        
        {
            (!isInitializing && !isLoadingRecommendation) ?
            <Animated.View className='absolute left-5 bottom-5' entering={menuButtonEnteringAnim}>
                <TailwindButton onPress={onMenuButtonPress} roundedClassName='rounded-xl' buttonStyleClassName={`p-3 ${TailwindClasses.ICON_BUTTON_SIZES}`}><MenuIcon width={32} height={32} fill={"#575757"} /></TailwindButton>
            </Animated.View> : null
        }
        
    </HillBackgroundView>
}