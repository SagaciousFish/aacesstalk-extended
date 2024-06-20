import { CardCategory, CardInfo, TopicCategory, appendCard, childCardSessionSelectors } from "@aacesstalk/libs/ts-core"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { VoiceOverManager } from "apps/client-rn/src/services/voiceover"
import { getTopicColorClassNames, styleTemplates } from "apps/client-rn/src/styles"
import { useNonNullUpdatedValue } from "apps/client-rn/src/utils/hooks"
import React from "react"
import { useCallback, useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Pressable, Text, View } from "react-native"
import Animated, { Easing, FlipInYLeft, FlipOutEasyY, interpolate, useAnimatedStyle, useSharedValue, withSpring, withTiming } from "react-native-reanimated"

export const CardCategoryView = (props: {
    topicCategory: TopicCategory,
    cardCategory: CardCategory,
    style?: any,
}) => {
    const {t} = useTranslation()

    const [_, lightTopicColor] = useMemo(()=>getTopicColorClassNames(props.topicCategory), [props.topicCategory])   

    const cardIds = useSelector(childCardSessionSelectors[props.cardCategory].selectIds)
    const cardEntities = useSelector(childCardSessionSelectors[props.cardCategory].selectEntities)

    const slicedCardIds = useMemo(()=>{
        const result: Array<Array<string>> = []
        for(let i = 0; i < cardIds.length; i += 2){
            result.push(cardIds.slice(i, i+2))
        }
        return result
    }, [cardIds])

    return <View className={`${lightTopicColor} rounded-2xl p-2`} style={props.style}>
        <Text style={styleTemplates.withBoldFont} className="text-lg text-center">{t(`Session.Cards.Category.${props.cardCategory}`)}</Text>
        

            {
                slicedCardIds.map((row, rowIndex) => <View key={rowIndex} className="flex-row">{
                    row.map((id,index) => {
                        const actualIndex = rowIndex * 2 + index
                        return <Animated.View 
                        key={cardEntities[id].label_localized}
                        entering={FlipInYLeft.duration(500).easing(Easing.elastic(0.7)).delay(200 + 200*actualIndex)}
                        exiting={FlipOutEasyY.duration(200).delay(200*actualIndex)}><TopicChildCardView key={id} id={id} category={props.cardCategory}/></Animated.View>})
                }</View>)
            }
    </View>
}


export const TopicChildCardView = (props:{
    category: CardCategory,
    id: string,
    cardClassName?: string
}) => {
    const dispatch = useDispatch()

    const cardInfo = useNonNullUpdatedValue(useSelector(state => childCardSessionSelectors[props.category].selectById(state, props.id)))
    const isProcessing = useSelector(state => state.session.isProcessingRecommendation)

    const token = useSelector(state => state.auth.jwt)

    const onPress = useCallback(async ()=>{
        dispatch(appendCard(cardInfo))
        // Play voice over
        await VoiceOverManager.instance.placeVoiceoverFetchTask(cardInfo, token)
    }, [cardInfo, token])

    return <ChildCardView disabled={isProcessing} label={cardInfo?.label_localized || cardInfo?.label} cardClassName={props.cardClassName} onPress={onPress}/>
}

export const ChildCardView = React.memo((props:{
    label: string,
    disabled?: boolean,
    onPress?: () => void,
    cardClassName?: string
}) => {


    const pressAnimProgress = useSharedValue(0)

    const onPressIn = useCallback(()=>{
        pressAnimProgress.value = withTiming(1, {duration: 200, easing: Easing.out(Easing.cubic)})
    }, [])

    const onPressOut = useCallback(()=>{
        pressAnimProgress.value = withSpring(0, {duration: 500})
    }, [])

    const containerAnimStyle = useAnimatedStyle(() => {
        return {
            transform: [
                {scale: interpolate(pressAnimProgress.value, [0, 1], [1, 0.95])},
                {translateY: interpolate(pressAnimProgress.value, [0, 1], [0, 10])}
        ] as any
        }
    }, [])

    const onPress = useCallback(()=>{
        props.onPress?.()
    }, [props.onPress])

    return <Pressable disabled={props.disabled} onPressIn={onPressIn} onPressOut={onPressOut} onPress={onPress}><Animated.View
        style={containerAnimStyle} className={`rounded-xl shadow-lg shadow-black/80 border-2 border-slate-200 p-2 bg-white w-[11vw] h-[11vw] m-2 ${props.cardClassName}`}>
        <View className="aspect-square bg-gray-200 flex-1 self-center"></View>
        <Text className="self-center mt-2 text-black/80" style={styleTemplates.withBoldFont}>{props.label}</Text>
    </Animated.View></Pressable>
})