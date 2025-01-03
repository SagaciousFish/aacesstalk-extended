import { styleTemplates } from "apps/client-rn/src/styles"
import { useCallback, useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Platform, Pressable, StyleSheet, Text, View, ViewStyle } from "react-native"
import Animated, { Easing, interpolate, useAnimatedStyle, useSharedValue, withSpring, withTiming } from "react-native-reanimated"
import stringFormat from 'pupa'
import { twMerge } from "tailwind-merge"

const styles = StyleSheet.create({
    buttonFrame: Platform.OS == 'android' ? {
        elevation: 10
    } : {
        shadowColor: "#000",
        shadowOffset: {
            width: 0,
            height: 10,
        },
        shadowOpacity: 0.2,
        shadowRadius: 10
    }
})

export const TopicButton = (props: {
    title: string,
    imageComponent: JSX.Element,
    buttonClassName?: string,
    disabled?: boolean,
    style?: any,
    imageContainerStyleDimensions: Pick<ViewStyle, "width"|"height"|"left"|"top"|"right"|"bottom">
    imageNormalDegree: number,
    imagePressedDegree: number,
    numSessionsToday?: number,
    numSessionsTotal?: number,
    onPress?: () => void,
}) => {

    const [t] = useTranslation()

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
        return Platform.OS == 'android' ? {
            elevation: interpolate(pressAnimProgress.value, [0, 1], [10, 2]),
            transform: [
                {scale: interpolate(pressAnimProgress.value, [0, 1], [1, 0.95])},
                {translateY: interpolate(pressAnimProgress.value, [0, 1], [0, 10])}
            ] as any
        } : {
            shadowRadius: interpolate(pressAnimProgress.value, [0, 1], [10, 2]),
            shadowOffset: {
                width: 0,
                height: interpolate(pressAnimProgress.value, [0, 1], [10, 2])
            }
        }
    }, [])

    const contentContainerAnimStyleIOS = useAnimatedStyle(() => {
        return {
            transform: [
                {scale: interpolate(pressAnimProgress.value, [0, 1], [1, 0.95])},
                {translateY: interpolate(pressAnimProgress.value, [0, 1], [0, 10])}
        ] as any
        }
    }, [])

    const imageContainerStyle = useAnimatedStyle(() => {
        return {
            position: 'absolute',
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

    const todayCountText = useMemo(()=>{
        if(props.numSessionsToday != null && props.numSessionsToday > 0){
            return stringFormat(t("Session.DialogueCountTodayTemplate"), {count: props.numSessionsToday})
        }else{
            return t("Session.DialogueCountTodayNone")
        }
    }, [t, props.numSessionsToday])

    const totalCountText = useMemo(()=>{
        if(props.numSessionsTotal != null && props.numSessionsTotal > 0){
            return stringFormat(t("Session.DialogueCountTotalTemplate"), {count: props.numSessionsTotal})
        }else{
            return t("Session.DialogueCountTotalNone")
        }
    }, [t, props.numSessionsTotal])

    const buttonViewClassName = useMemo(()=>{
        return twMerge("w-[32vh] h-[32vh] rounded-[28px] border-[5px] border-white bg-teal-400 block relative px-5 py-6 pb-4 overflow-hidden", 
            props.buttonClassName, 
            props.disabled === true ? 'opacity-50' : '')
    }, [props.buttonClassName, props.disabled])

    const content = <Pressable accessible={false} style={Platform.OS == 'android' ? props.style : undefined} onPressIn={onPressIn} onPressOut={onPressOut} onPress={props.onPress} disabled={props.disabled}>
    <Animated.View className={buttonViewClassName} style={Platform.OS == 'android'? [styles.buttonFrame, containerAnimStyle] : contentContainerAnimStyleIOS}>
        <Animated.View style={imageContainerStyle} className="bottom-[25%]">
            {props.imageComponent}
        </Animated.View>
        <Text style={styleTemplates.withExtraboldFont} className="text-white text-2xl flex-1" numberOfLines={3}>{props.title}</Text>
        {
            (props.numSessionsToday != null || props.numSessionsTotal != null) ? <View className="absolute bottom-4 left-4">
                { props.numSessionsToday != null && (props.numSessionsTotal != null && props.numSessionsTotal > 0) ? <Text style={styleTemplates.withSemiboldFont} className="text-white text-md">{todayCountText}</Text> : null}
                { props.numSessionsTotal != null ? <Text style={styleTemplates.withSemiboldFont} className="text-white text-md mt-1">{totalCountText}</Text> : null}
                
            </View> : null
        }
    </Animated.View>
</Pressable>

    if(Platform.OS == 'android'){
        return content
    }else{
        return <Animated.View style={[props.style, styles.buttonFrame, containerAnimStyle]} >
            {content}
            </Animated.View>
    }
}