import { useCallback, useLayoutEffect, useState } from 'react'
import {Image, LayoutChangeEvent} from 'react-native'
import { Easing, interpolate, useAnimatedStyle, useSharedValue, withDelay, withSequence, withTiming } from 'react-native-reanimated'
import Reanimated from 'react-native-reanimated'

const AnimatedImage = Reanimated.createAnimatedComponent(Image)

export const TurnStar = (props: {
    style?: any,
    starClassName?: string,
    useEnteringAttentionAnimation?: boolean,
    enteringAnimationDelay?: number
}) => {

    const attentionAnimProgress = useSharedValue(props.useEnteringAttentionAnimation ? 0: 1)

    const attentionAnimMovementProgress = useSharedValue(0)

    const [viewHeight, setViewHeight] = useState(0)

    const style = useAnimatedStyle(()=>{


        return {
            opacity: interpolate(attentionAnimProgress.value, [0, 0.05], [0, 1]),
            transform: [
                {rotateY: `${interpolate(attentionAnimProgress.value, [0,1], [0, 360*3])}deg`},
                {translateY: interpolate(attentionAnimMovementProgress.value, [0, 1], [0, -viewHeight])},
                {scale: interpolate(attentionAnimMovementProgress.value, [0, 1], [1, 1.3])}
            ]
        } as any
    }, [viewHeight])

    useLayoutEffect(()=>{
        if(props.useEnteringAttentionAnimation){
            attentionAnimProgress.value = withDelay(props.enteringAnimationDelay || 0, withTiming(1, {duration: 4000}))
            attentionAnimMovementProgress.value = withDelay(props.enteringAnimationDelay || 0, withSequence(
                withTiming(0.8, {duration: 300, easing: Easing.out(Easing.quad)}),
                withTiming(0, {duration: 1500, easing: Easing.in(Easing.bounce)}),
            ))
        }
    }, [props.useEnteringAttentionAnimation, props.enteringAnimationDelay])

    const onLayout = useCallback((event: LayoutChangeEvent)=>{
        setViewHeight(event.nativeEvent.layout.height)
    }, [])

    return <AnimatedImage onLayout={onLayout} style={[props.style, style]} source={require('../../../assets/images/feedback-star.png')} className={`w-16 h-16 ${props.starClassName}`}/>
}