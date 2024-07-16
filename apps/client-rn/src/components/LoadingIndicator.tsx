import { Text, View, Image } from "react-native"
import CircleSnail from 'react-native-progress/CircleSnail'
import { styleTemplates } from "../styles"
import { TopicCategory } from "@aacesstalk/libs/ts-core"
import { useEffect, useMemo, useState } from "react"
import { shuffle } from 'fast-shuffle'

const colors = require("../styles/colors")

const loadingImages = require("./loading-images.js")

const shuffledLoadingImages = shuffle(loadingImages)
let pointer = -1
function getNextLoadingImage(): any{
    pointer = (++pointer) % loadingImages.length
    return shuffledLoadingImages[pointer]
}

export const LoadingIndicator = (
    props: {
        label: string,
        containerClassName?: string,
        titleClassName?: string,
        color?: string,
        colorTopic?: TopicCategory,
        horizontal?: boolean,
        useImage?: boolean
    }
) => {

    const color = useMemo(()=>{
        if(props.color != null){
             return props.color
        }else if(props.colorTopic != null){
            return colors["topic" + props.colorTopic]["fg"]
        }else return "#808080"
    }, [props.color, props.colorTopic])

    const useImage = useMemo(()=>{
        return props.useImage === true && loadingImages.length > 0
    }, [props.useImage])

    const [imageSource, setImageSource] = useState(undefined)

    useEffect(()=>{
        if(useImage == true){
            setImageSource(getNextLoadingImage())
        }else{
            setImageSource(undefined)
        }
    }, [useImage])

    return <View className={`items-center p-4 ${props.containerClassName} ${props.horizontal === true ? "flex-row" : "flex-col"} ${useImage === true ? 'bg-white rounded-2xl p-4 shadow-lg shadow-black/60':''}`}>
        {
            useImage == true && imageSource != null ? <Image className="w-[250px] h-[250px]" source={imageSource}/> : <CircleSnail size={props.horizontal ? 40 : 60} spinDuration={2000} duration={1000} thickness={5} color={color}/>
        }
        
        <Text style={styleTemplates.withBoldFont} className={`text-xl mt-3 ${props.horizontal === true ? "mt-0 ml-2" : ""} ${props.titleClassName}`}>{props.label}</Text>
    </View>
}