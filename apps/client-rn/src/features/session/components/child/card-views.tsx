import { CardCategory, TopicCategory } from "@aacesstalk/libs/ts-core"
import { useSelector } from "apps/client-rn/src/redux/hooks"
import { getTopicColors, styleTemplates } from "apps/client-rn/src/styles"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Text, View } from "react-native"

export const CardCategoryView = (props: {
    topicCategory: TopicCategory,
    cardCategory: CardCategory,
    style?: any,
}) => {
    const {t} = useTranslation()

    const [_, lightTopicColor] = useMemo(()=>getTopicColors(props.topicCategory), [props.topicCategory])   

    const cardIds = useSelector(state => state.session.childCardEntityStateByCategory[props.cardCategory].ids)

    const slicedCardIds = useMemo(()=>{
        const result: Array<Array<string>> = []
        for(let i = 0; i < cardIds.length; i += 2){
            result.push(cardIds.slice(i, i+2))
        }
        return result
    }, [cardIds])

    return <View className={`${lightTopicColor} rounded-2xl p-2`} style={props.style}>
        <Text style={styleTemplates.withBoldFont} className="text-lg text-center">{t(`Session.Cards.Category.${props.cardCategory}`)}</Text>
        

            {
                slicedCardIds.map((row, rowIndex) => <View key={rowIndex} className="flex-row">{
                    row.map(id => <ChildCardView key={id} id={id} category={props.cardCategory}/>)
                }</View>)
            }
    </View>
}

export const ChildCardView = (props:{
    category: CardCategory,
    id: string,
    cardClassName?: string
}) => {
    const cardInfo = useSelector(state => state.session.childCardEntityStateByCategory[props.category].entities[props.id])

    return <View className={`rounded-xl shadow-lg shadow-black/80 border-2 border-slate-200 p-2 bg-white w-[11vw] h-[11vw] m-2 ${props.cardClassName}`}>
        <View className="aspect-square bg-gray-200 flex-1 self-center"></View>
        <Text className="self-center mt-2 text-black/80" style={styleTemplates.withBoldFont}>{cardInfo.label_localized}</Text>
    </View>
}