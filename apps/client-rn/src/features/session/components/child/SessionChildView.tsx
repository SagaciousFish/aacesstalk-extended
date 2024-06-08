import { CardCategory } from "@aacesstalk/libs/ts-core"
import { LoadingIndicator } from "apps/client-rn/src/components/LoadingIndicator"
import { useSelector } from "apps/client-rn/src/redux/hooks"
import { useTranslation } from "react-i18next"
import { View } from "react-native"
import format from 'string-template'
import { CardCategoryView, ChildCardView } from "./card-views"
import { SelectedCardDeck } from "./SelectedCardDeck"

const MAIN_CATEGORIES = [CardCategory.Topic, CardCategory.Action, CardCategory.Emotion]

const CoreCardsDeck = () => {
    
    const coreCardIds = useSelector(state => state.session.childCardEntityStateByCategory[CardCategory.Core].ids)
    
    return <View className="flex-row justify-center">{
        coreCardIds.map(id => <ChildCardView key={id} id={id} category={CardCategory.Core} cardClassName="w-[10vw] h-[10vw]"/>)
        }</View>
}

export const SessionChildView = () => {
    const child_name = useSelector(state => state.auth.dyadInfo?.child_name)
    const topic = useSelector(state => state.session.topic)
    const isProcessing = useSelector(state => state.session.isProcessingRecommendation)
    
    const {t} = useTranslation()

    return <View className="flex-1 self-stretch items-center justify-between pb-4">
        {
            isProcessing === true ? <View pointerEvents="none" className="absolute top-0 bottom-0 left-0 right-0 z-3 bg-white/50 justify-center"><LoadingIndicator containerClassName="self-center" colorTopic={topic?.category} label={format(t("Session.LoadingMessage.ChildCardsTemplate"), {child_name})}/></View> : 
            <>
                <SelectedCardDeck topicCategory={topic.category}/>
                <View id="main-category-cards" className="flex-row self-stretch justify-evenly px-14">
                {
                    MAIN_CATEGORIES.map(cardCategory => {
                        return <CardCategoryView key={cardCategory} topicCategory={topic.category} cardCategory={cardCategory}/>
                    })
                }
                </View>
                <CoreCardsDeck/>
            </>
        }
        </View>
}