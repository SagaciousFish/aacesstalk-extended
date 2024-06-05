import { Text, View } from "react-native"
import CircleSnail from 'react-native-progress/CircleSnail'
import { styleTemplates } from "../styles"
import { TopicCategory } from "@aacesstalk/libs/ts-core"
import { useMemo } from "react"
const colors = require("../styles/colors")

export const LoadingIndicator = (
    props: {
        label: string,
        containerClassName?: string,
        titleClassName?: string,
        color?: string,
        colorTopic?: TopicCategory,
        horizontal?: boolean,
    }
) => {

    const color = useMemo(()=>{
        if(props.color != null){
             return props.color
        }else if(props.colorTopic != null){
            return colors["topic" + props.colorTopic]["fg"]
        }else return "#808080"
    }, [props.color, props.colorTopic])

    return <View className={`items-center p-4 ${props.containerClassName} ${props.horizontal === true ? "flex-row" : "flex-col"}`}>
        <CircleSnail size={props.horizontal ? 40 : 60} spinDuration={2000} duration={1000} thickness={5} color={color}/>
        <Text style={styleTemplates.withBoldFont} className={`text-xl mt-3 ${props.horizontal === true ? "mt-0 ml-2" : ""} ${props.titleClassName}`}>{props.label}</Text>
    </View>
}