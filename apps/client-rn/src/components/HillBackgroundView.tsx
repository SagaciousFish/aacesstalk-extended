import { StyleSheet, View, useWindowDimensions } from "react-native"

import HillImage from '../assets/images/hill-normal.svg'
import Cloud1Image from '../assets/images/cloud-1.svg'
import Cloud2Image from '../assets/images/cloud-2.svg'

const styles = StyleSheet.create({
    hill: {
        position: 'absolute',
        bottom: 0
    },
    cloud1: {
        position: 'absolute',
        zIndex: -1,
        right: -50,
        top: '35%'
    },
    cloud2: {
        position: 'absolute',
        zIndex: -1,
        left: 50,
        top: '20%'
    }
})

export const HillBackgroundView = (props: {containerClassName?: string, children?: any}) => {

    const {width, height} = useWindowDimensions()

    const hillHeight = 255/1194 * width

    return <View className={`flex-1 ${props.containerClassName} bg-[#EDFAFF]`}>
        {props.children}
        <HillImage width={width} height={hillHeight} pointerEvents={"none"} style={styles.hill}/>
        <Cloud1Image width={344} height={230} style={styles.cloud1}/>

        <Cloud2Image width={213} height={146} style={styles.cloud2}/>
    </View>
}