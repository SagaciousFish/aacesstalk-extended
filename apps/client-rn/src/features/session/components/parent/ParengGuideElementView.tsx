import { requestParentGuideExampleMessage } from "@aacesstalk/libs/ts-core";
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useCallback, useMemo } from "react";
import { Pressable, Text } from "react-native"
import Animated ,{ Easing, ZoomIn, interpolate, useAnimatedStyle, useSharedValue, withSpring, withTiming } from 'react-native-reanimated';

export const ParentGuideElementView = (props: {
    id: string,
    order: number
}) => {
    const dispatch = useDispatch()

    const topicCategory = useSelector(state => state.session.topic.category)
    const guide = useSelector(state => state.session.parentGuideEntityState.entities[props.id])
    const isExampleLoading = useSelector(state => state.session.parentExampleMessageLoadingFlags[props.id] || false)
    const exampleMessage = useSelector(state => state.session.parentExampleMessages[props.id])

    console.log(isExampleLoading, props.id, exampleMessage)

    const enteringAnim = useMemo(() => ZoomIn.springify().duration(600).delay(props.order * 100), [props.order])

    const pressAnimProgress = useSharedValue(0)

    const onPressIn = useCallback(()=>{
        if(exampleMessage == null && isExampleLoading === false){
            pressAnimProgress.value = withTiming(1, {duration: 200, easing: Easing.out(Easing.cubic)})
        }
    }, [isExampleLoading, exampleMessage])

    const onPressOut = useCallback(()=>{
        if(exampleMessage == null && isExampleLoading === false){
            pressAnimProgress.value = withSpring(0, {duration: 500})
        }
    }, [isExampleLoading, exampleMessage])

    const onPress = useCallback(()=>{
        if(exampleMessage == null && isExampleLoading === false){
            dispatch(requestParentGuideExampleMessage(props.id))
        }
    }, [props.id, isExampleLoading, exampleMessage])

    const containerAnimStyle = useAnimatedStyle(() => {
        return {
            transform: [
                {scale: interpolate(pressAnimProgress.value, [0, 1], [1, 0.90])},
                {translateY: interpolate(pressAnimProgress.value, [0, 1], [0, 5])}
        ] as any
        }
    }, [])
    
    return <Pressable onPress={onPress} onPressIn={onPressIn} onPressOut={onPressOut}><Animated.View entering={enteringAnim} style={containerAnimStyle} className={`bg-topic${topicCategory}-fg w-[70vw] h-[16vh] justify-center px-8 rounded-2xl border-white border-[4px] shadow-lg shadow-slate-800/60`}>
        <Text style={styleTemplates.withSemiboldFont} className="text-2xl text-white text-center">{guide.guide_localized}</Text>
        </Animated.View></Pressable>
}