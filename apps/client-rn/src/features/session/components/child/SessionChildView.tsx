import { CardCategory } from "@aacesstalk/libs/ts-core"
import { LoadingIndicator } from "apps/client-rn/src/components/LoadingIndicator"
import { useSelector } from "apps/client-rn/src/redux/hooks"
import { useTranslation } from "react-i18next"
import { View } from "react-native"
import format from 'string-template'
import { CardCategoryView, ChildCardView, TopicChildCardView } from "./card-views"
import { SelectedCardDeck } from "./SelectedCardDeck"
import { useMemo } from "react"
import Animated, { FadeIn, FadeOut } from 'react-native-reanimated'

const MAIN_CATEGORIES = [CardCategory.Topic, CardCategory.Action, CardCategory.Emotion]

const CoreCardsDeck = () => {
    
    const coreCardIds = useSelector(state => state.session.childCardEntityStateByCategory[CardCategory.Core].ids)
    
    return <View className="flex-row justify-center">{
        coreCardIds.map(id => <TopicChildCardView key={id} id={id} category={CardCategory.Core} cardClassName="w-[10vw] h-[10vw]"/>)
        }</View>
}

export const SessionChildView = () => {
    const child_name = useSelector(state => state.auth.dyadInfo?.child_name)
    const topic = useSelector(state => state.session.topic)
    const isProcessing = useSelector(state => state.session.isProcessingRecommendation)
    const latestChildCardRecommendationId = useSelector(state => state.session.childCardRecommendationId)
    
    const {t} = useTranslation()

    const loadingMessage = useMemo(()=> {
        if(latestChildCardRecommendationId == null){
            return format(t("Session.LoadingMessage.ChildCardsTemplate"), {child_name})
        }else{
            return t("Session.LoadingMessage.RefreshChildCards")
        }
        
    }, [latestChildCardRecommendationId])

    return <View className="flex-1 self-stretch items-center justify-between pb-4">
        {latestChildCardRecommendationId != null ? <>
            <SelectedCardDeck topicCategory={topic.category}/>
            <View id="main-category-cards" className="flex-row self-stretch justify-evenly px-14">
                {
                    MAIN_CATEGORIES.map(cardCategory => {
                    return <CardCategoryView key={cardCategory} topicCategory={topic.category} cardCategory={cardCategory}/>
                })
            }
            </View>
            <CoreCardsDeck/>
        </> : null}
        {
            isProcessing === true ? <Animated.View entering={FadeIn.duration(400)} exiting={FadeOut.duration(300)} className={`absolute ${latestChildCardRecommendationId == null ? "top-0" : "top-[14vw]"} bottom-0 left-0 right-0 z-3 bg-white/70 justify-center`}>
                <LoadingIndicator containerClassName="self-center" colorTopic={topic?.category} label={loadingMessage}/>
            </Animated.View> : null
        }
        </View>
}