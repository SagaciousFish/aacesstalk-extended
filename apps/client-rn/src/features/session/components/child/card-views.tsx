import { CardCategory, CardInfo, TopicCategory, appendCard } from "@aacesstalk/libs/ts-core"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { getTopicColorClassNames, styleTemplates } from "apps/client-rn/src/styles"
import { useCallback, useEffect, useMemo, useState } from "react"
import { useTranslation } from "react-i18next"
import { Pressable, Text, View } from "react-native"
import { Reanimated } from "react-native-gesture-handler/lib/typescript/handlers/gestures/reanimatedWrapper"
import Animated, { Easing, FlipInEasyY, FlipInYLeft, FlipInYRight, FlipOutEasyY, SlideInRight, SlideOutLeft, interpolate, useAnimatedStyle, useSharedValue, withSpring, withTiming } from "react-native-reanimated"

export const CardCategoryView = (props: {
    topicCategory: TopicCategory,
    cardCategory: CardCategory,
    style?: any,
}) => {
    const {t} = useTranslation()

    const [_, lightTopicColor] = useMemo(()=>getTopicColorClassNames(props.topicCategory), [props.topicCategory])   

    const cardIds = useSelector(state => state.session.childCardEntityStateByCategory[props.cardCategory].ids)
    const cardEntities = useSelector(state => state.session.childCardEntityStateByCategory[props.cardCategory].entities)

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

    const cardInfo = useSelector(state => state.session.childCardEntityStateByCategory[props.category].entities[props.id])
    const isProcessing = useSelector(state => state.session.isProcessingRecommendation)

    const onPress = useCallback(()=>{
        dispatch(appendCard(cardInfo))
    }, [cardInfo])

    return <ChildCardView key={cardInfo.label_localized} disabled={isProcessing} cardInfo={cardInfo} cardClassName={props.cardClassName} onPress={onPress}/>
}

export const ChildCardView = (props:{
    cardInfo: CardInfo,
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

    return <Pressable disabled={props.disabled} onPressIn={onPressIn} onPressOut={onPressOut} onPress={props.onPress}><Animated.View
        style={containerAnimStyle} className={`rounded-xl shadow-lg shadow-black/80 border-2 border-slate-200 p-2 bg-white w-[11vw] h-[11vw] m-2 ${props.cardClassName}`}>
        <View className="aspect-square bg-gray-200 flex-1 self-center"></View>
        <Text className="self-center mt-2 text-black/80" style={styleTemplates.withBoldFont}>{props.cardInfo.label_localized}</Text>
    </Animated.View></Pressable>
}