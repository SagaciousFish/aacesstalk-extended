import {StyleSheet} from 'react-native'
import { TopicCategory, removeLastCard, selectedChildCardSelectors } from '@aacesstalk/libs/ts-core'
import { useDispatch, useSelector } from 'apps/client-rn/src/redux/hooks'
import { getTopicColorClassNames, getTopicColors, styleTemplates } from 'apps/client-rn/src/styles'
import { useCallback, useEffect, useMemo, useRef } from 'react'
import {View} from 'react-native'
import { ChildCardView } from './card-views'
import { TailwindButton } from 'apps/client-rn/src/components/tailwind-components'
import { RemoveCardIcon } from 'apps/client-rn/src/components/vector-icons'
import Animated, { Easing, FlipInXUp, FlipOutXDown, LinearTransition } from 'react-native-reanimated'
import { VoiceOverManager } from 'apps/client-rn/src/services/voiceover'
import { ScrollView } from 'react-native-gesture-handler'
import usePrevious from 'apps/client-rn/src/utils/hooks'

const styles = StyleSheet.create({
    cardScrollViewContentContainerStyle: {...styleTemplates.itemsCenter, flexGrow: 1, paddingRight: 120}
})

const SelectedCardView = (props: {
    id: string,
    disabled?: boolean
}) => {

    const cardInfo = useSelector(state => selectedChildCardSelectors.selectById(state, props.id))
    const token = useSelector(state => state.auth.jwt)

    const onPress = useCallback(async ()=>{
        await VoiceOverManager.instance.placeVoiceoverFetchTask(cardInfo, token)
    }, [cardInfo?.id, cardInfo?.recommendation_id, token])

    return <ChildCardView label={cardInfo?.label_localized} disabled={props.disabled} onPress={onPress}/>
}

const selectedCardEnteringAnim = FlipInXUp.duration(300).springify()
const selectedCardExitingAnim = FlipOutXDown.duration(400).easing(Easing.in(Easing.back(1.7)))


export const SelectedCardDeck = (props: {
    topicCategory: TopicCategory
}) => {

    const dispatch = useDispatch()

    const [_, lightTopicColorClassName] = useMemo(()=>getTopicColorClassNames(props.topicCategory), [props.topicCategory])

    const scrollViewRef = useRef<ScrollView>(null)

    const selectedCardIds = useSelector(selectedChildCardSelectors.selectIds)

    const previousSelectedCardCount = usePrevious(selectedCardIds.length)

    const isInteractionEnabled = useSelector(state => state.session.isProcessingRecommendation === false)

    const removeButtonColor = useMemo(()=> getTopicColors(props.topicCategory).fg, [props.topicCategory])
    const panelBackgroundColor = useMemo(()=> getTopicColors(props.topicCategory).dimmed, [props.topicCategory])

    const onPressRemove = useCallback(()=>{
        scrollViewRef.current?.scrollToEnd({animated: true})
        dispatch(removeLastCard())
    }, [])

    useEffect(()=>{
        if(previousSelectedCardCount != selectedCardIds.length){
            requestAnimationFrame(()=>{
                scrollViewRef.current?.scrollToEnd({animated: true})
            })
            
        }
    }, [previousSelectedCardCount, selectedCardIds.length])

    return <View className={`self-stretch h-[14vw] ${lightTopicColorClassName} flex-row items-stretch relative`}>
        <ScrollView ref={scrollViewRef} nestedScrollEnabled={false} horizontal className='flex-1' 
            contentContainerStyle={styles.cardScrollViewContentContainerStyle}
            endFillColor={panelBackgroundColor}
            fadingEdgeLength={200}
            >
        {
            selectedCardIds.map(id => <Animated.View entering={selectedCardEnteringAnim} exiting={selectedCardExitingAnim} layout={LinearTransition.duration(300)} key={id}>
                <SelectedCardView id={id} disabled={!isInteractionEnabled}/>
                </Animated.View>)
        }
        </ScrollView>
        {
            selectedCardIds.length >= 1 ?<View className='absolute right-0 top-0 bottom-0'><TailwindButton containerClassName='self-center' disabled={!isInteractionEnabled} buttonStyleClassName='self-stretch flex-1 bg-transparent' onPress={onPressRemove}>
                <RemoveCardIcon fill={removeButtonColor}/>
            </TailwindButton></View> : null
        }
    </View>
}