import { TopicCategory, removeLastCard } from '@aacesstalk/libs/ts-core'
import { useDispatch, useSelector } from 'apps/client-rn/src/redux/hooks'
import { getTopicColorClassNames, getTopicColors } from 'apps/client-rn/src/styles'
import { useCallback, useMemo } from 'react'
import {View} from 'react-native'
import { ChildCardView } from './card-views'
import { TailwindButton } from 'apps/client-rn/src/components/tailwind-components'
import { RemoveCardIcon } from 'apps/client-rn/src/components/vector-icons'
import Animated, { Easing, FlipInXUp, FlipOutXDown } from 'react-native-reanimated'

const SelectedCardView = (props: {
    id: string,
    disabled?: boolean
}) => {

    const cardInfo = useSelector(state => state.session.selectedChildCardEntityState.entities[props.id])

    return <ChildCardView cardInfo={cardInfo} disabled={props.disabled}/>
}

const selectedCardEnteringAnim = FlipInXUp.duration(300).springify()
const selectedCardExitingAnim = FlipOutXDown.duration(400).easing(Easing.in(Easing.back(1.7)))


export const SelectedCardDeck = (props: {
    topicCategory: TopicCategory
}) => {

    const dispatch = useDispatch()

    const [_, lightTopicColorClassName] = useMemo(()=>getTopicColorClassNames(props.topicCategory), [props.topicCategory])


    const selectedCardIds = useSelector(state => state.session.selectedChildCardEntityState.ids)

    const isInteractionEnabled = useSelector(state => state.session.isProcessingRecommendation === false)

    const removeButtonColor = useMemo(()=> getTopicColors(props.topicCategory).bg, [props.topicCategory])

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