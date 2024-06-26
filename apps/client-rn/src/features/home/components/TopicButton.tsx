import { styleTemplates } from "apps/client-rn/src/styles"
import { useCallback } from "react"
import { Pressable, Text, ViewStyle } from "react-native"
import Animated, { Easing, interpolate, useAnimatedStyle, useSharedValue, withSpring, withTiming } from "react-native-reanimated"

export const TopicButton = (props: {
    title: string,
    dialogueCount: number,
    imageComponent: JSX.Element,
    buttonClassName?: string,
    disabled?: boolean,
    style?: any,
    imageContainerStyleDimensions: Pick<ViewStyle, "width"|"height"|"left"|"top"|"right"|"bottom">
    imageNormalDegree: number,
    imagePressedDegree: number,
    onPress?: () => void
}) => {

    const pressAnimProgress = useSharedValue(0)
    const pressAnimImageProgress = useSharedValue(0)

    const onPressIn = useCallback(()=>{
        pressAnimProgress.value = withTiming(1, {duration: 200, easing: Easing.out(Easing.cubic)})
        pressAnimImageProgress.value = withTiming(1, {duration: 300, easing: Easing.out(Easing.cubic)})
    }, [])

    const onPressOut = useCallback(()=>{
        pressAnimProgress.value = withSpring(0, {duration: 500})
        pressAnimImageProgress.value = withSpring(0, {duration: 300})
    }, [])

    const containerAnimStyle = useAnimatedStyle(() => {
        return {
            transform: [
                {scale: interpolate(pressAnimProgress.value, [0, 1], [1, 0.95])},
                {translateY: interpolate(pressAnimProgress.value, [0, 1], [0, 10])}
        ] as any
        }
    }, [])

    const imageContainerStyle = useAnimatedStyle(() => {
        return {
            position: 'absolute', zIndex: -1,
            width: '55%', 
            height: '55%',
            opacity: 0.1,
            ...props.imageContainerStyleDimensions,
            transform: [
                {scale: interpolate(pressAnimProgress.value, [0, 1], [1, 0.8])},
                {translateY: interpolate(pressAnimImageProgress.value, [0, 1], [0, 10])},
                {rotate: `${interpolate(pressAnimImageProgress.value, [0, 1], [props.imageNormalDegree, props.imagePressedDegree])}deg`} as any
            ]
        }
    }, [props.imageContainerStyleDimensions, props.imageNormalDegree, props.imagePressedDegree])

    return <Pressable style={props.style} onPressIn={onPressIn} onPressOut={onPressOut} onPress={props.onPress} disabled={props.disabled}>
            <Animated.View className={`w-[32vh] h-[32vh] rounded-[28px] border-[5px] border-white shadow-2xl shadow-slate-600 bg-teal-400 block ${props.buttonClassName} relative px-5 py-6 pb-4 overflow-hidden ${props.disabled === true ? 'opacity-50' : ''}`} style={containerAnimStyle}>
            <Text style={styleTemplates.withExtraboldFont} className="text-white text-2xl">{props.title}</Text>
            <Animated.View style={imageContainerStyle} className="bottom-[25%]">
                {props.imageComponent}
            </Animated.View>
        </Animated.View>
        </Pressable>
}