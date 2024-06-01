import { StyleSheet, View, useWindowDimensions } from "react-native"
import Reanimated, { Easing, interpolate, useAnimatedStyle, useSharedValue, withRepeat, withTiming } from 'react-native-reanimated'

import HillImage from '../assets/images/hill-normal.svg'
import Cloud1Image from '../assets/images/cloud-1.svg'
import Cloud2Image from '../assets/images/cloud-2.svg'
import { useEffect } from "react"

const styles = StyleSheet.create({
    hill: {
        zIndex: -1,
        position: 'absolute',
        bottom: 0
    },
    cloud1: {
        position: 'absolute',
        zIndex: -2,
        right:50,
        top: '40%'
    },
    cloud2: {
        position: 'absolute',
        zIndex: -3,
        left: 40,
        top: '20%'
    },
    cloud3: {
        position: 'absolute',
        zIndex: -4,
        opacity: 0.7,
        left: '45%',
        top: '-50%',
    }
})

export const HillBackgroundView = (props: {
    containerClassName?: string, 
    hillComponentClass?: any, hillImageWidth?: number, hillImageHeight?: number, 
    children?: any}) => {

    const {width, height} = useWindowDimensions()

    const hillHeight = (props.hillImageHeight || 255)/(props.hillImageWidth || 1194) * width

    const cloud1PositionCycle = useSharedValue(0);
    const cloud2PositionCycle = useSharedValue(0);

    const cloud3PositionCycle = useSharedValue(0);
    
   
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



    const cloud3Style = useAnimatedStyle(() => {
        return {
            ...styles.cloud3,
            transform: [
                {translateX: interpolate(cloud3PositionCycle.value, [0, 1], [0, width])},
            ]
        }
    }, [width])

    const cloud3_1Style = useAnimatedStyle(() => {
        return {
            ...styles.cloud3,
            transform: [
                {translateX: interpolate(cloud3PositionCycle.value, [0, 1], [-width, 0])},
            ]
        }
    }, [width])

    useEffect(()=>{
        cloud1PositionCycle.value = withRepeat(withTiming(1, {duration: 16000, easing: Easing.linear}), -1, false)

        cloud2PositionCycle.value = withRepeat(withTiming(1, {duration: 14000, easing: Easing.linear}), -1, false)

        cloud3PositionCycle.value = withRepeat(withTiming(1, {duration: 30000, easing: Easing.linear}), -1, false)
    }, [])
    
    const HillComponent = props.hillComponentClass || HillImage

    return <View className={`flex-1 bg-[#EDFAFF] ${props.containerClassName}`}>
        {props.children}
        <HillComponent width={width} height={hillHeight} pointerEvents={"none"} style={styles.hill}/>
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

        <Reanimated.View style={cloud3Style} pointerEvents={"none"}>
            <Cloud1Image width={600} height={500} />
        </Reanimated.View>

        <Reanimated.View style={cloud3_1Style} pointerEvents={"none"}>
            <Cloud1Image width={600} height={500} />
        </Reanimated.View>
    </View>
}