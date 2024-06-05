import { useMemo } from "react"
import { Gesture, GestureDetector } from "react-native-gesture-handler"

export const MultiTapButton = (props: {
    numberOfTaps: number,
    onTapGesture: () => void,
    children?: any
}) => {

    const tripleTap = useMemo(()=>Gesture.Tap().maxDuration(600).numberOfTaps(props.numberOfTaps)
    .onStart(props.onTapGesture), [props.onTapGesture])
    
    return <GestureDetector gesture={tripleTap}>{props.children}</GestureDetector>
}