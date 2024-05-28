import { StyleSheet, View, useWindowDimensions } from "react-native"
import Reanimated, { Easing, interpolate, useAnimatedStyle, useSharedValue, withRepeat, withTiming } from 'react-native-reanimated'

import HillImage from '../assets/images/hill-normal.svg'
import Cloud1Image from '../assets/images/cloud-1.svg'
import Cloud2Image from '../assets/images/cloud-2.svg'
import { useEffect } from "react"

const styles = StyleSheet.create({
    hill: {
        position: 'absolute',
        bottom: 0
    },
    cloud1: {
        position: 'absolute',
        zIndex: -1,
        right:50,
        top: '35%'
    },
    cloud2: {
        position: 'absolute',
        zIndex: -1,
        left: 40,
        top: '20%'
    }
})

export const HillBackgroundView = (props: {containerClassName?: string, children?: any}) => {

    const {width, height} = useWindowDimensions()

    const hillHeight = 255/1194 * width

    const cloud1PositionCycle = useSharedValue(0);
    const cloud2PositionCycle = useSharedValue(0);
    
   
    const cloud1Style = useAnimatedStyle(() => {
        return {
            ...styles.cloud1,
            transform: [{translateX: interpolate(cloud1PositionCycle.value, [0, 1], [0, width])}]   
        }
    }, [width])


    const cloud1_1Style = useAnimatedStyle(() => {
        return {
            ...styles.cloud1,
            transform: [{translateX: interpolate(cloud1PositionCycle.value, [0, 1], [-width, 0])}]   
        }
    }, [width])

    const cloud2Style = useAnimatedStyle(() => {
        return {
            ...styles.cloud2,
            transform: [{translateX: interpolate(cloud2PositionCycle.value, [0, 1], [0, width])}]   
        }
    }, [width])

    const cloud2_1Style = useAnimatedStyle(() => {
        return {
            ...styles.cloud2,
            transform: [{translateX: interpolate(cloud2PositionCycle.value, [0, 1], [-width, 0])}]   
        }
    }, [width])

    useEffect(()=>{
        cloud1PositionCycle.value = withRepeat(withTiming(1, {duration: 15000, easing: Easing.linear}), -1, false)

        cloud2PositionCycle.value = withRepeat(withTiming(1, {duration: 12000, easing: Easing.linear}), -1, false)
    }, [])


    return <View className={`flex-1 ${props.containerClassName} bg-[#EDFAFF]`}>
        {props.children}
        <HillImage width={width} height={hillHeight} pointerEvents={"none"} style={styles.hill}/>
        <Reanimated.View style={cloud1Style} pointerEvents={"none"}>
            <Cloud1Image width={344} height={230} />
        </Reanimated.View>
        <Reanimated.View style={cloud1_1Style} pointerEvents={"none"}>
            <Cloud1Image width={344} height={230} />
        </Reanimated.View>
        <Reanimated.View style={cloud2Style} pointerEvents={"none"}>
            <Cloud2Image width={213} height={146} />
        </Reanimated.View>

        <Reanimated.View style={cloud2_1Style} pointerEvents={"none"}>
            <Cloud2Image width={213} height={146} />
        </Reanimated.View>
    </View>
}