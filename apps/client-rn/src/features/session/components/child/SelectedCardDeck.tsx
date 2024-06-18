import { TopicCategory, removeLastCard, selectSelectedChildCardById, selectSelectedChildCardIds } from '@aacesstalk/libs/ts-core'
import { useDispatch, useSelector } from 'apps/client-rn/src/redux/hooks'
import { getTopicColorClassNames, getTopicColors } from 'apps/client-rn/src/styles'
import { useCallback, useMemo } from 'react'
import {View} from 'react-native'
import { ChildCardView } from './card-views'
import { TailwindButton } from 'apps/client-rn/src/components/tailwind-components'
import { RemoveCardIcon } from 'apps/client-rn/src/components/vector-icons'
import Animated, { Easing, FlipInXUp, FlipOutXDown } from 'react-native-reanimated'
import { VoiceOverManager } from 'apps/client-rn/src/services/voiceover'

const SelectedCardView = (props: {
    id: string,
    disabled?: boolean
}) => {

    const cardInfo = useSelector(state => selectSelectedChildCardById(state, props.id))
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


    const selectedCardIds = useSelector(selectSelectedChildCardIds)

    const isInteractionEnabled = useSelector(state => state.session.isProcessingRecommendation === false)

    const removeButtonColor = useMemo(()=> getTopicColors(props.topicCategory).fg, [props.topicCategory])

    const onPressRemove = useCallback(()=>{
        dispatch(removeLastCard())
    }, [])

    return <View className={`self-stretch h-[14vw] ${lightTopicColorClassName} flex-row items-center`}>
        {
            selectedCardIds.map(id => <Animated.View entering={selectedCardEnteringAnim} exiting={selectedCardExitingAnim} key={id}>
                <SelectedCardView id={id} disabled={!isInteractionEnabled}/>
                </Animated.View>)
        }
        {
            selectedCardIds.length >= 1 ? <><View className='flex-1'/>
            <TailwindButton disabled={!isInteractionEnabled} buttonStyleClassName='self-stretch flex-1 bg-transparent' onPress={onPressRemove}>
                <RemoveCardIcon fill={removeButtonColor}/>
            </TailwindButton></> : null
        }
    </View>
}