import { styleTemplates } from "apps/client-rn/src/styles"
import { useCallback } from "react"
import { Pressable, Text, View } from "react-native"
import Animated, { Easing, interpolate, useAnimatedStyle, useSharedValue, withSpring, withTiming } from "react-native-reanimated"

export const TopicButton = (props: {
    title: string,
    dialogueCount: number,
    imageComponent?: JSX.Element,
    buttonClassName?: string,
    style?: any
}) => {

    const pressAnimProgress = useSharedValue(0)

    const onPressIn = useCallback(()=>{
        pressAnimProgress.value = withTiming(1, {duration: 200, easing: Easing.out(Easing.cubic)})
    }, [])

    const onPressOut = useCallback(()=>{
        pressAnimProgress.value = withSpring(0, {duration: 500})
    }, [])

    const onPress = useCallback(()=>{
        console.log("onPress")
    }, [])

    const containerAnimStyle = useAnimatedStyle(() => {
        return {
            transform: [
                {scale: interpolate(pressAnimProgress.value, [0, 1], [1, 0.95])},
                {translateY: interpolate(pressAnimProgress.value, [0, 1], [0, 10])}
        ] as any
        }
    }, [])

    return <Pressable style={props.style} onPressIn={onPressIn} onPressOut={onPressOut} onPress={onPress}>
            <Animated.View className={`w-[32vh] h-[32vh] rounded-[28px] border-[5px] border-white shadow-2xl shadow-slate-600 bg-teal-400 block ${props.buttonClassName} relative px-5 py-6 pb-4 overflow-hidden`} style={containerAnimStyle}>
            <Text style={styleTemplates.withExtraboldFont} className="text-white text-2xl">{props.title}</Text>
            <View style={{position: 'absolute', zIndex: -1, left: -25, top: 40, width: 200, height: 200, transform: [{rotate: "10deg"}, {scale: 0.57}], opacity: 0.2}}>
                {props.imageComponent}
            </View>
        </Animated.View>
        </Pressable>
}