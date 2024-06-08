import { TopicCategory } from '@aacesstalk/libs/ts-core'
import { getTopicColors } from 'apps/client-rn/src/styles'
import { useMemo } from 'react'
import {View} from 'react-native'

export const SelectedCardDeck = (props: {
    topicCategory: TopicCategory
}) => {

    const [_, lightTopicColor] = useMemo(()=>getTopicColors(props.topicCategory), [props.topicCategory]) 

    return <View className={`self-stretch h-[14vw] ${lightTopicColor}`}></View>
}