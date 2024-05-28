import { ButtonProps, Pressable, View, Text, ViewStyle, PressableAndroidRippleConfig } from "react-native";
import { styleTemplates } from "../styles";
import { useMemo } from "react";

export const TailwindButton = (props: {
    containerClassName?: string
    roundedClassName?: string
    buttonStyleClassName?: string
    disabledButtonStyleClassName?: string
    titleClassName?: string,
    rippleColor?: string
} & ButtonProps) => {

    const rippleConfig = useMemo(()=>{
        return {color: props.rippleColor || "##F9AA3330"}
    }, [props.rippleColor])

    return <View className={`overflow-hidden ${props.roundedClassName} ${props.containerClassName}`} removeClippedSubviews={true}>
        <Pressable disabled={props.disabled} android_ripple={rippleConfig} onPress={props.onPress} 
        className={`items-center flex-row justify-center px-8 py-3 bg-white shadow-lg shadow-slate-500/50 ${props.buttonStyleClassName} ${props.roundedClassName} ${props.disabled === true ? props.disabledButtonStyleClassName : ""}`}>
    <Text className={`text-lg text-center ${props.titleClassName}`} style={styleTemplates.withBoldFont}>{props.title}</Text>
</Pressable></View>
}