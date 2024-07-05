import { NativeStackScreenProps } from "@react-navigation/native-stack"
import { PopupMenuScreenFrame } from "apps/client-rn/src/components/PopupMenuScreenFrame"
import { MainRoutes } from "apps/client-rn/src/navigation"
import { useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useCallback, useMemo } from "react"
import { Text, View } from "react-native"
import { ScrollView } from "react-native-gesture-handler"
import { dailyStarStatsSelector } from "../selectors"
import moment from "moment-timezone"
import { useTranslation } from "react-i18next"
import stringTemplate from 'string-template'
import { TurnStar } from "../../session/components/TurnStar"

export const DailySummaryElement = (props: {
    dateString: string
    numStars: number
    numDialogues: number
}) => {

    const [t] = useTranslation()

    const dateText = useMemo(()=>{
        const m = moment(props.dateString, "YYYY-MM-DD")
        const ymd = stringTemplate(t("Summary.DateTemplate"), {year: m.format("YYYY"), month: m.format("M"), date: m.format("D")})
        const dow = t(`Summary.DayOfWeek.${m.day().toString()}`)

        return ymd + " " + dow
    }, [props.dateString, t])

    const numStarsLoopArray = useMemo(()=>{
        return new Array(props.numStars).fill(null)
    }, [props.numStars])

    return <View className="flex-row items-center border-b-2 border-slate-200 px-10 py-3">
        <Text style={styleTemplates.withSemiboldFont} className="text-3xl w-[36%] my-5">{dateText}</Text>
        <Text style={styleTemplates.withSemiboldFont} className="text-2xl w-[12%]">대화 {props.numDialogues}회</Text>
        <View className="flex-row flex-wrap gap-2 items-center">{
            numStarsLoopArray.map((_,i) =>  <TurnStar key={i} starClassName="w-10 h-10"/>)}</View>
    </View>
}

export const StarListScreen = (props: NativeStackScreenProps<MainRoutes.MainNavigatorParamList, "stars">) => {

    const {summaryList, totalStars} = useSelector(dailyStarStatsSelector)

    const [t] = useTranslation()

    const closeScreen = useCallback(()=>{
        props.navigation.pop()
    }, [props.navigation])

    return <PopupMenuScreenFrame onPop={closeScreen} dismissOnPressOutside={true} panelClassName="max-w-full h-[90vh] w-[90vw]">
        
        <View className="flex-row items-center px-10 pb-6 mt-2 border-b-2 border-slate-300">
            <Text style={styleTemplates.withBoldFont} className="text-4xl flex-1">{t('Summary.StarsTitle')}</Text>
            <View className="flex-row items-center">
               <TurnStar starClassName="w-10 h-10"/>
               <Text style={styleTemplates.withExtraboldFont} className="ml-4 mt-[5px] text-3xl text-orange-400">{ stringTemplate(t("Summary.StarsCountUnitTemplate"), {stars: totalStars}) }</Text>
            </View>
            
        </View>
        <ScrollView>
            {
                summaryList.map(s => {
                    return <DailySummaryElement key={s.dateString} dateString={s.dateString} numStars={s.numStarsTotal} numDialogues={s.numDialogues}/>
                })
            }
        </ScrollView>
    </PopupMenuScreenFrame>
}