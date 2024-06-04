import { ParentGuideCategory, ParentGuideType, requestParentGuideExampleMessage } from "@aacesstalk/libs/ts-core";
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useCallback, useEffect, useMemo } from "react";
import { Pressable, Text, View, StyleSheet } from "react-native"
import Animated ,{ Easing, ZoomIn, interpolate, interpolateColor, useAnimatedStyle, useSharedValue, withSpring, withTiming } from 'react-native-reanimated';

const styles = StyleSheet.create({
    guideFrame: {
        shadowColor: "rgba(0,0,50,0.5)",
        shadowOffset: {width: 10, height: 10},
        shadowRadius: 10,
        elevation: 10
    }
})

interface Props{id: string, order: number}

const TEXT_MESSAGE_CLASSNAME = "text-2xl text-white text-center"

const GUIDE_FRAME_DIMENSION_CLASSNAME = "w-[70vw] h-[16vh]"

const GUIDE_FRAME_CLASSNAME = `absolute ${GUIDE_FRAME_DIMENSION_CLASSNAME} justify-center px-8 rounded-2xl border-white border-[4px]`

export const ParentGuideElementView = (props: Props) => {
    const guideType = useSelector(state => state.session.parentGuideEntityState.entities[props.id].type)

    switch(guideType){
        case ParentGuideType.Messaging:
            return <ParentMessageGuideElementView id={props.id} order={props.order} />
        case ParentGuideType.Feedback:
            return <ParentFeedbackElementView id={props.id} order={props.order}/>
    }
}

const ParentMessageGuideElementView = (props: Props) => {
    const dispatch = useDispatch()

    const topicCategory = useSelector(state => state.session.topic.category)
    const guideMessage = useSelector(state => state.session.parentGuideEntityState.entities[props.id].guide_localized || state.session.parentGuideEntityState.entities[props.id].guide)
    const isExampleLoading = useSelector(state => state.session.parentExampleMessageLoadingFlags[props.id] || false)
    const exampleMessage = useSelector(state => state.session.parentExampleMessages[props.id])

    const enteringAnim = useMemo(() => ZoomIn.springify().duration(600).delay(props.order * 100), [props.order])

    const pressAnimProgress = useSharedValue(0)


    const exampleTransitionAnimProgress = useSharedValue(0)

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

    const runFlipAnim = useCallback(()=>{
        exampleTransitionAnimProgress.value = withTiming(1, {duration: 800, easing: Easing.elastic(1)})
    }, [])

    const onPress = useCallback(()=>{
        if(exampleMessage == null && isExampleLoading === false){
            dispatch(requestParentGuideExampleMessage(props.id, runFlipAnim))
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

    const guideMessageAnimStyle = useAnimatedStyle(()=>{
        return {
            opacity: interpolate(exampleTransitionAnimProgress.value, [0,1], [1,0], 'clamp'),
            shadowColor: interpolateColor(exampleTransitionAnimProgress.value,[0, 0.2], ["rgba(0,0,50,0.3)", "rgba(0,0,50,0)"], "RGB"),
            transform: [
                {rotateY: `${interpolate(exampleTransitionAnimProgress.value,[0, 1], [0, 180])}deg`}
            ]
        }
    }, [])

    const exampleMessageAnimStyle = useAnimatedStyle(()=>{
        return {
            shadowColor: interpolateColor(exampleTransitionAnimProgress.value,[0.8, 1], ["rgba(0,0,50,0)", "rgba(0,0,50,0.3)"], "RGB"),
            opacity: interpolate(exampleTransitionAnimProgress.value, [0,1], [0,1], 'clamp'),
            transform: [
                {rotateY: `${interpolate(exampleTransitionAnimProgress.value,[0, 1], [180, 360])}deg`}
            ]
        }
    }, [])

    console.log(`bg-topic${topicCategory}-light ${GUIDE_FRAME_CLASSNAME}`)
    
    return <Animated.View entering={enteringAnim}>
            <Pressable onPress={onPress} onPressIn={onPressIn} onPressOut={onPressOut} >
                <Animated.View style={containerAnimStyle} className={`${GUIDE_FRAME_DIMENSION_CLASSNAME}`}>
                    <Animated.View style={[styles.guideFrame, guideMessageAnimStyle]} className={`${GUIDE_FRAME_CLASSNAME} bg-topic${topicCategory}-fg`}>
                        <Text style={styleTemplates.withSemiboldFont} className={TEXT_MESSAGE_CLASSNAME}>{guideMessage}</Text>
                    </Animated.View>
                    <Animated.View style={[styles.guideFrame, exampleMessageAnimStyle]} className={`${GUIDE_FRAME_CLASSNAME} bg-topic${topicCategory}-dimmed`}>
                        <Text style={styleTemplates.withSemiboldFont} className={TEXT_MESSAGE_CLASSNAME}>{exampleMessage?.message_localized || exampleMessage?.message}</Text>
                    </Animated.View>
                </Animated.View>
            </Pressable>
        </Animated.View>
}

const ParentFeedbackElementView = (props: Props) => {

    const guideMessage = useSelector(state => state.session.parentGuideEntityState.entities[props.id].guide_localized || state.session.parentGuideEntityState.entities[props.id].guide)
    
    return <View key="message-view" className={`bg-white ${GUIDE_FRAME_CLASSNAME}`}>
            <Text style={styleTemplates.withSemiboldFont} className={TEXT_MESSAGE_CLASSNAME}>{guideMessage}</Text>
        </View>
}