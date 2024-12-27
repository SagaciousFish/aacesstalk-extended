import { ButtonProps, Pressable, View, Text, ViewStyle, PressableAndroidRippleConfig, PressableProps } from "react-native";
import { styleTemplates } from "../styles";
import { useMemo } from "react";

export const TailwindButton = (props: {
    containerClassName?: string
    roundedClassName?: string
    buttonStyleClassName?: string
    disabledButtonStyleClassName?: string
    disabledTitleClassName?: string
    titleClassName?: string,
    rippleColor?: string,
    shadowClassName?: string,
    title?: string,
    children?: any
} & Omit<ButtonProps, "title"> & PressableProps) => {

    const rippleConfig = useMemo(()=>{
        return {color: props.rippleColor || "##f9aa3330"}
    }, [props.rippleColor])

    console.log(`text-lg text-center text-slate-600 ${props.titleClassName} ${props.disabled === true ? (props.disabledTitleClassName || "") : ""}`)

    return <View accessible={false} className={`overflow-hidden ${props.shadowClassName || "shadow-lg shadow-slate-500/50"} ${props.roundedClassName} ${props.containerClassName}`} removeClippedSubviews={true}>
        <Pressable accessible={false} aria-selected={false} disabled={props.disabled} android_ripple={rippleConfig} onPress={props.onPress} onLongPress={props.onLongPress}
        className={`items-center flex-row justify-center px-8 py-3 bg-white ${props.buttonStyleClassName} ${props.roundedClassName} ${props.disabled === true ? (props.disabledButtonStyleClassName || "") : ""}`}>
            {
                props.children || <Text className={`text-lg text-center text-slate-600 ${props.titleClassName || ""} ${props.disabled === true ? (props.disabledTitleClassName || "") : ""}`} style={styleTemplates.withBoldFont}>{props.title}</Text>
            }
        </Pressable></View>
}