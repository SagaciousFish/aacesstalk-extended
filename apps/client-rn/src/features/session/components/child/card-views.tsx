import { CardCategory, CardImageMatching, CardInfo, Http, TopicCategory, appendCard, childCardSessionSelectors } from "@aacesstalk/libs/ts-core"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { CardImageManager } from "apps/client-rn/src/services/card-image"
import { VoiceOverManager } from "apps/client-rn/src/services/voiceover"
import { getTopicColorClassNames, styleTemplates } from "apps/client-rn/src/styles"
import { useNonNullUpdatedValue, usePrevious } from "apps/client-rn/src/utils/hooks"
import React, { forwardRef, Fragment, useEffect, useLayoutEffect, useRef, useState } from "react"
import { useCallback, useMemo } from "react"
import { useTranslation } from "react-i18next"
import { LayoutChangeEvent, Platform, Pressable, StyleSheet, Text, View, ViewProps, ViewStyle } from "react-native"
import Animated, { cancelAnimation, Easing, Extrapolation, FlipInYLeft, FlipOutEasyY, interpolate, measure, runOnJS, runOnUI, useAnimatedStyle, useSharedValue, withDelay, withSpring, withTiming } from "react-native-reanimated"
import { FasterImageView, ImageOptions } from '@candlefinance/faster-image';
import { twMerge } from "tailwind-merge"
import { current } from "tailwindcss/colors"


const styles = StyleSheet.create({
    cardFrame: {
        shadowColor: "rgba(10,10,10)",
        shadowOpacity: 0.2,
        shadowOffset: {width: 0, height: 5},
        shadowRadius: 2.6,
        elevation: 4,
    },
    imageView: {aspectRatio: 1, flex:1, alignSelf: 'center', borderRadius: 8, overflow: 'hidden'},

    hidden: {opacity: 0},
    shown: {opacity: 1}
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

    return <View className={`rounded-2xl p-2`} style={props.style}>
        <Text style={styleTemplates.withBoldFont} className="text-lg text-center">{t(`Session.Cards.Category.${props.cardCategory}`)}</Text>        
        

            {
                slicedCardIds.map((row, rowIndex) => <View key={rowIndex} className="flex-row">{
                    row.map((id,index) => {
                        const actualIndex = rowIndex * 2 + index
                        /*
                        <Animated.View 
                                    key={id}
                                    entering={FlipInYLeft.duration(500).easing(Easing.elastic(0.7)).delay(200 + 200*actualIndex)}
                                    exiting={FlipOutEasyY.duration(200).delay(200*actualIndex)}>
                               </Animated.View>*/
                        return <TopicChildCardView key={actualIndex} id={id} renderOrder={actualIndex} category={props.cardCategory}/>})
                }</View>)
            }
    </View>
}

export const TopicChildCardView = (props:{
    category: CardCategory,
    id: string,
    renderOrder?: number,
    cardClassName?: string,
    useFlipAnim?: boolean
}) => {
    const dispatch = useDispatch()

    const cardInfo = useSelector(state => childCardSessionSelectors[props.category].selectById(state, props.id))
    const isProcessing = useSelector(state => state.session.isProcessingRecommendation)

    const token = useSelector(state => state.auth.jwt)

    const onPress = useCallback(async ()=>{
        dispatch(appendCard(cardInfo))
        // Play voice over
        await VoiceOverManager.instance.placeVoiceoverFetchTask(cardInfo, token)
    }, [cardInfo, token])

    const label = cardInfo?.label_localized || cardInfo?.label

    const prevId = usePrevious(props.id)
    const prevLabel = usePrevious(label)

    // Card Flipping ===============================================================================
    
    const [isFlipping, setIsFlipping] = useState<boolean>(false)

    const flipAnimProgress = useSharedValue(0)

    const startFlipAnim = useCallback(()=>{
        flipAnimProgress.set(0)
        setIsFlipping(true)
        flipAnimProgress.value = withDelay(200 + 200*(props.renderOrder || 0), withTiming(1, {
            duration: 2000,
            easing: Easing.elastic(1)
        }, ()=>{
            runOnJS(setIsFlipping)(false)
            flipAnimProgress.set(0)
        }))
    }, [setIsFlipping, props.renderOrder])



    useEffect(()=>{
        if(prevId != null && prevId != props.id && prevLabel != label){
            //Card flip required
            console.log("Flip card")
            startFlipAnim()
        }
    }, [prevId, props.id, prevLabel, label, props.renderOrder, startFlipAnim])

    // Flipped card style =============================================================================


    const mainCardViewRef = useRef(null)

    const [cardSize, setCardSize] = useState<{width: number, height: number}>(undefined)

    useLayoutEffect(()=>{
        if(mainCardViewRef.current){
            mainCardViewRef.current?.measureInWindow((x, y, width, height) => {
                console.log(width, height)
                setCardSize({width, height})
            });
        }
        //const rect = mainCardViewRef.current?.getBoundingClientRect?.();
        //console.log(rect)
    }, [setCardSize])


    const flipCardDefaultStyle = useMemo<ViewStyle>(()=>({
        ...styles.cardFrame,
        position: 'absolute', 
        zIndex: 1,
        width: cardSize?.width, 
        height: cardSize?.height
    }), [cardSize])

    const foreCardAnimatedStyle = useAnimatedStyle(()=>{
        return {
            opacity: interpolate(flipAnimProgress.value, [0,0.5], [1,0], Extrapolation.CLAMP),
            transform: [
                {perspective: 1000},
                {rotateY: `${interpolate(flipAnimProgress.value, [0, 1], [0, 180])}deg`}
            ] as any
        }
    }, [flipCardDefaultStyle])


    //=================================================================================================

    if(props.useFlipAnim === false) {
        return <ClickableChildCardView disabled={isProcessing} 
        imageQueryId={props.id} 
        label={label} 
        cardClassName={props.cardClassName} onPress={onPress}/>
    }else { 
        return <View>
                    <ChildCardViewContent label={prevLabel} imageQueryId={prevId} animatedStyle={[flipCardDefaultStyle, foreCardAnimatedStyle]}/>
                    <ClickableChildCardView ref={mainCardViewRef} disabled={isProcessing}
                    containerStyle={isFlipping === true ? styles.hidden : styles.shown}
                    imageQueryId={props.id} 
                    label={label} 
                    cardClassName={props.cardClassName} onPress={onPress}/>
            </View>   
    }
}



export const ChildCardViewContent = forwardRef((props:{
    label: string,
    imageQueryId?: string,
    cardClassName?: string,
    style?: ViewStyle,
    animatedStyle?: any
}, ref) => {

    const token = useSelector(state => state.auth.jwt)

    const [imageSource, setImageSource] = useState<ImageOptions>(undefined)

    const applyCardImage = useCallback(async (matching: CardImageMatching) => {
        const headers = await Http.getSignedInHeaders(token)

        setImageSource({
            headers,
            transitionDuration: 0,
            url: Http.axios.defaults.baseURL + Http.ENDPOINT_DYAD_MEDIA_CARD_IMAGE + "?card_type=" + matching.type + "&image_id=" + matching.image_id,
        } as ImageOptions)
    }, [token])

    const cardFrameClassName = useMemo(()=>{
        return twMerge('rounded-xl border-2 border-slate-200 pt-1 pb-[3px] bg-white w-[11vw] h-[11vw] m-1.5', props.cardClassName)
    }, [props.cardClassName])

    useEffect(()=>{
        if(props.imageQueryId){
            const cached = CardImageManager.instance.getCachedMatching(props.imageQueryId)
            if(cached){
                applyCardImage(cached)
            }

            CardImageManager.instance.subscribeToImageMatching(props.imageQueryId, applyCardImage)
        }
    }, [props.imageQueryId, applyCardImage])

    return <Animated.View ref={ref as any}
            style={[props.style, props.animatedStyle]} className={cardFrameClassName}>
            <FasterImageView style={styles.imageView} source={imageSource}/>
            <Text className="self-center mt-2 text-black/80 text-center" style={styleTemplates.withBoldFont}>{props.label}</Text>
    </Animated.View>
})



export const ClickableChildCardView = forwardRef((props:{
    label: string,
    imageQueryId?: string,
    disabled?: boolean,
    onPress?: () => void,
    cardClassName?: string,
    containerStyle?: ViewStyle
}, ref) => {

    const pressAnimProgress = useSharedValue(0)

    const onPressIn = useCallback(()=>{
        pressAnimProgress.value = withTiming(1, {duration: 200, easing: Easing.out(Easing.cubic)})
    }, [])

    const onPressOut = useCallback(()=>{
        pressAnimProgress.value = withSpring(0, {duration: 500})
    }, [])

    const cardFrameAnimStyle = useAnimatedStyle(() => {
        const shadowStyle = Platform.OS == 'ios' ? {
            ...styles.cardFrame,
            shadowOffset: {width: 0, height: interpolate(pressAnimProgress.value, [0, 1], [styles.cardFrame.shadowOffset.height, 2])},
            shadowRadius: interpolate(pressAnimProgress.value, [0, 1], [styles.cardFrame.shadowRadius, 1]),
        } : {
            elevation: interpolate(pressAnimProgress.value, [0, 1], [styles.cardFrame.elevation, 1]),
        }
        
        return {
            ...shadowStyle,            
            transform: [
                {scale: interpolate(pressAnimProgress.value, [0, 1], [1, 0.95])},
                {translateY: interpolate(pressAnimProgress.value, [0, 1], [0, 10])}
        ] as any
        }
    }, [])

    const onPress = useCallback(()=>{
        props.onPress?.()
    }, [props.onPress])

    return <Pressable style={props.containerStyle} accessible={false} disabled={props.disabled} onPressIn={onPressIn} onPressOut={onPressOut} onPress={onPress}>
        <ChildCardViewContent {...props} ref={ref as any} animatedStyle={cardFrameAnimStyle}/>
        </Pressable>
})