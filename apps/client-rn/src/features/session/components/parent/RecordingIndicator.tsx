import { useSelector } from "apps/client-rn/src/redux/hooks"
import {Text, View} from 'react-native'
import { RecordingStatus } from "../../../audio/reducer"
import { useTranslation } from "react-i18next"
import { styleTemplates } from "apps/client-rn/src/styles"
import Reanimated, { Easing, Extrapolation, interpolate, runOnJS, useAnimatedStyle, useSharedValue, withRepeat, withSpring, withTiming } from "react-native-reanimated"
import { useEffect, useState } from "react"

export const RecordingIndicator = () => {

    const audioRecordingStatus = useSelector(state => state.parentAudioRecording.status)
    const audioRecordingMeter = useSelector(state => state.parentAudioRecording.recordingMeter)

    const [t] = useTranslation()

    const appearProgress = useSharedValue(0)

    const meteringValue = useSharedValue(-100)

    const labelAnimValue = useSharedValue(1)

    const [shown, setShown] = useState(false)

    const containerAnimStyle = useAnimatedStyle(()=>{
        return {
            transform: [
                {scale: interpolate(appearProgress.value, [0, 1], [0, 1], Extrapolation.CLAMP)}
            ]
        }
    }, [])

    const meteringAnimStyle = useAnimatedStyle(()=>{
        return {
            transform: [
                {scale: interpolate(meteringValue.value, [-80, 0], [0, 1], Extrapolation.CLAMP)}
            ]
        }
    }, [])

    const labelAnimStyle = useAnimatedStyle(()=>{
        return {
            opacity: interpolate(labelAnimValue.value, [0, 1], [0.4, 1], Extrapolation.CLAMP)
        }
    }, [])

    useEffect(()=>{
        meteringValue.value = withTiming(audioRecordingMeter, {duration: 100, easing: Easing.elastic(0.1)})
    }, [audioRecordingMeter])
    
    useEffect(()=>{
        if(audioRecordingStatus == RecordingStatus.Recording){
            setShown(true)
            appearProgress.value = withSpring(1, {duration: 400})
        }else{
            appearProgress.value = withTiming(0, {duration: 300, easing: Easing.out(Easing.quad)}, () => {
                runOnJS(()=>{
                    setShown(false)
                })
            })
        }
    }, [audioRecordingStatus])

    useEffect(()=>{
        labelAnimValue.value = withRepeat(withTiming(0, {duration: 1000}), null, true)
    }, [])

    return <Reanimated.View style={containerAnimStyle} pointerEvents="none" className={`absolute top-5 left-5 px-3 py-1.5 bg-white/80 rounded-lg flex-row items-center gap-x-2 ${shown ? '' : 'hidden'}`}>
        <View className="bg-transparent w-6 h-6 rounded-full border-[1.5px] border-red-300 items-center justify-center">
            <Reanimated.View className="w-6 h-6 bg-red-400 rounded-full scale-50" style={meteringAnimStyle}/>
        </View>
        <Reanimated.Text style={[styleTemplates.withSemiboldFont, labelAnimStyle]} className="text-lg">{t("Session.ParentMessage.Recording")}</Reanimated.Text>
    </Reanimated.View>
}