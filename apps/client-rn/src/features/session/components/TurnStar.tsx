import { useEffect, useLayoutEffect } from 'react'
import {View, Image} from 'react-native'
import { interpolate, useAnimatedStyle, useSharedValue, withTiming } from 'react-native-reanimated'
import Reanimated from 'react-native-reanimated'

const AnimatedImage = Reanimated.createAnimatedComponent(Image)

export const TurnStar = (props: {
    style?: any,
    starClassName?: string,
    useEnteringAttentionAnimation?: boolean
}) => {

    const attentionAnimProgress = useSharedValue(props.useEnteringAttentionAnimation ? 0: 1)

    const style = useAnimatedStyle(()=>{
        return {
            opacity: interpolate(attentionAnimProgress.value, [0, 0.1], [0, 1]),
            transform: [
                {rotateY: `${interpolate(attentionAnimProgress.value, [0,1], [0, 360*5])}deg`}
            ]
        } as any
    }, [])

    useLayoutEffect(()=>{
        if(props.useEnteringAttentionAnimation){
            attentionAnimProgress.value = withTiming(1, {duration: 4000})
        }
    }, [props.useEnteringAttentionAnimation])

    return <AnimatedImage style={[props.style, style]} source={require('../../../assets/images/feedback-star.png')} className={`w-16 h-16 ${props.starClassName}`}/>
}