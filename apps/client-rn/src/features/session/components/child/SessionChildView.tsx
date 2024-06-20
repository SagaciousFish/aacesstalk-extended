import { CardCategory, DialogueRole, refreshCards } from "@aacesstalk/libs/ts-core"
import { LoadingIndicator } from "apps/client-rn/src/components/LoadingIndicator"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { useTranslation } from "react-i18next"
import { View } from "react-native"
import format from 'string-template'
import { CardCategoryView, TopicChildCardView } from "./card-views"
import { SelectedCardDeck } from "./SelectedCardDeck"
import { useCallback, useEffect, useMemo } from "react"
import Animated, { FadeIn, FadeOut, LayoutAnimationConfig } from 'react-native-reanimated'
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components"
import { RefreshIcon } from "apps/client-rn/src/components/vector-icons"
import { TailwindClasses } from "apps/client-rn/src/styles"
import { VoiceOverManager } from "apps/client-rn/src/services/voiceover"
import { useNonNullUpdatedValue } from "apps/client-rn/src/utils/hooks"

const MAIN_CATEGORIES = [CardCategory.Topic, CardCategory.Action, CardCategory.Emotion]

const CoreCardsDeck = () => {
    
    const coreCardIds = useSelector(state => state.session.childCardEntityStateByCategory[CardCategory.Core].ids)
    
    return <View className="flex-row justify-center">{
        coreCardIds.map(id => <TopicChildCardView key={id} id={id} category={CardCategory.Core} cardClassName="w-[10vw] h-[10vw]"/>)
        }</View>
}

const RefreshButton = () => {

    const isProcessing = useSelector(state => state.session.isProcessingRecommendation)

    const dispatch = useDispatch()

    const onPress = useCallback(() => {
        dispatch(refreshCards())
    }, [])

    return <TailwindButton disabled={isProcessing} containerClassName="absolute bottom-5 right-5" roundedClassName='rounded-xl' buttonStyleClassName={`p-3 ${TailwindClasses.ICON_BUTTON_SIZES}`} onPress={onPress}>
        <RefreshIcon width={28} height={28} fill={"#575757"} />
    </TailwindButton>
}

export const SessionChildView = () => {
    const child_name = useNonNullUpdatedValue(useSelector(state => state.auth.dyadInfo?.child_name))
    const topic = useNonNullUpdatedValue(useSelector(state => state.session.topic))
    const isProcessing = useSelector(state => state.session.isProcessingRecommendation)
    const latestChildCardRecommendationId = useSelector(state => state.session.childCardRecommendationId)

    const currentTurn = useSelector(state => state.session.currentTurn)
    
    const {t} = useTranslation()

    const loadingMessage = useMemo(()=> {
        if(latestChildCardRecommendationId == null){
            return format(t("Session.LoadingMessage.ChildCardsTemplate"), {child_name})
        }else{
            return t("Session.LoadingMessage.RefreshChildCards")
        }
        
    }, [latestChildCardRecommendationId])

    useEffect(()=>{
        return () => {
            VoiceOverManager.instance.cancelAll()
        }
    }, [])

    return <View className="flex-1 self-stretch items-center justify-between pb-4">
        {latestChildCardRecommendationId != null ? <>
            <SelectedCardDeck topicCategory={topic.category}/>
            <View id="main-category-cards" className="flex-row self-stretch justify-evenly px-14">
                <LayoutAnimationConfig skipExiting={true}>{
                    MAIN_CATEGORIES.map(cardCategory => {
                        return <CardCategoryView key={cardCategory} topicCategory={topic.category} cardCategory={cardCategory}/>
                    })
                }</LayoutAnimationConfig>
            </View>
            <CoreCardsDeck/>
            <RefreshButton/>
        </> : null}
        {
            isProcessing === true ? <Animated.View entering={FadeIn.duration(400)} exiting={FadeOut.duration(300)} className={`absolute ${latestChildCardRecommendationId == null ? "top-0" : "top-[14vw]"} bottom-0 left-0 right-0 z-3 bg-white/70 justify-center`}>
                <LoadingIndicator containerClassName="self-center" colorTopic={topic?.category} label={loadingMessage}/>
            </Animated.View> : null
        }
        </View>
}