import { useMemo } from "react"
import { Gesture, GestureDetector } from "react-native-gesture-handler"
import { runOnJS } from "react-native-reanimated"

export const MultiTapButton = (props: {
    numberOfTaps: number,
    onTapGesture: () => void,
    children?: any
}) => {

    const tripleTap = useMemo(()=>Gesture.Tap().runOnJS(true).maxDuration(600).numberOfTaps(props.numberOfTaps)
    .onStart(props.onTapGesture), [props.onTapGesture])
    
    return <GestureDetector gesture={tripleTap}>{props.children}</GestureDetector>
}