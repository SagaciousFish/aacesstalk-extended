import { CardCategory, CardImageMatching, CardInfo, Http, TopicCategory, appendCard, childCardSessionSelectors } from "@aacesstalk/libs/ts-core"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { CardImageManager } from "apps/client-rn/src/services/card-image"
import { VoiceOverManager } from "apps/client-rn/src/services/voiceover"
import { getTopicColorClassNames, styleTemplates } from "apps/client-rn/src/styles"
import { useNonNullUpdatedValue } from "apps/client-rn/src/utils/hooks"
import React, { useEffect, useState } from "react"
import { useCallback, useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Pressable, StyleSheet, Text, View } from "react-native"
import Animated, { Easing, FlipInYLeft, FlipOutEasyY, interpolate, useAnimatedStyle, useSharedValue, withSpring, withTiming } from "react-native-reanimated"
import { FasterImageView, ImageOptions } from '@candlefinance/faster-image';


const styles = StyleSheet.create({
    imageView: {aspectRatio: 1, flex:1, alignSelf: 'center'}
})

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
                        key={id}
                        entering={FlipInYLeft.duration(500).easing(Easing.elastic(0.7)).delay(200 + 200*actualIndex)}
                        exiting={FlipOutEasyY.duration(200).delay(200*actualIndex)}><TopicChildCardView id={id} category={props.cardCategory}/></Animated.View>})
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

    return <ChildCardView disabled={isProcessing} imageQueryId={props.id} label={cardInfo?.label_localized || cardInfo?.label} cardClassName={props.cardClassName} onPress={onPress}/>
}

export const ChildCardView = React.memo((props:{
    label: string,
    imageQueryId?: string,
    disabled?: boolean,
    onPress?: () => void,
    cardClassName?: string
}) => {

    const token = useSelector(state => state.auth.jwt)

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

    const [imageSource, setImageSource] = useState<ImageOptions>(undefined)

    const applyCardImage = useCallback(async (matching: CardImageMatching) => {
        const headers = await Http.getSignedInHeaders(token)

        setImageSource({
            headers,
            url: Http.axios.defaults.baseURL + Http.ENDPOINT_DYAD_MEDIA_CARD_IMAGE + "?card_type=" + matching.type + "&image_id=" + matching.image_id,
        } as ImageOptions)
    }, [token])

    useEffect(()=>{
        if(props.imageQueryId){
            const cached = CardImageManager.instance.getCachedMatching(props.imageQueryId)
            if(cached){
                applyCardImage(cached)
            }

            CardImageManager.instance.subscribeToImageMatching(props.imageQueryId, applyCardImage)
        }
    }, [props.imageQueryId, applyCardImage])

    return <Pressable accessible={false} disabled={props.disabled} onPressIn={onPressIn} onPressOut={onPressOut} onPress={onPress}><Animated.View
        style={containerAnimStyle} className={`rounded-xl shadow-lg shadow-black/80 border-2 border-slate-200 p-0 pb-[3px] bg-white w-[11vw] h-[11vw] m-1.5 ${props.cardClassName}`}>
        <FasterImageView style={styles.imageView} source={imageSource}/>
        <Text className="self-center mt-2 text-black/80 text-center" style={styleTemplates.withBoldFont}>{props.label}</Text>
    </Animated.View></Pressable>
})