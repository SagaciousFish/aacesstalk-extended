import { TopicCategory, endSession } from "@aacesstalk/libs/ts-core"
import { useFocusEffect } from "@react-navigation/native"
import { NativeStackScreenProps } from "@react-navigation/native-stack"
import { MainRoutes } from "apps/client-rn/src/navigation"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { useDisableBack, useNonNullUpdatedValue } from "apps/client-rn/src/utils/hooks"
import { useCallback, useMemo, useState } from "react"
import { Text, View, Image } from "react-native"
import { SessionTitleRibbon } from "../components/parent/SessionTitleRibbon"
import { useTranslation } from "react-i18next"
import { getTopicColorClassNames, styleTemplates } from "apps/client-rn/src/styles"
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components"

export const SessionClosingScreen = (props: NativeStackScreenProps<MainRoutes.MainNavigatorParamList, "session-closing">) => {

    useDisableBack()

    const routeSessionId = props.route.params.sessionId

    const routeNumStars = props.route.params.numStars
    
    const systemSessionId = useSelector(state => state.session.id)
    const numStarsLoopArray = useMemo(()=>{
        return new Array(routeNumStars).fill(null)
    }, [routeNumStars])
    const topic = useNonNullUpdatedValue(useSelector(state => state.session.topic))

    const dispatch = useDispatch()

    const [t] = useTranslation()

    const [canClose, setCanClose] = useState(false)

    const [topicColorFG, topicColorDimmed] = useMemo(()=>getTopicColorClassNames(topic?.category || TopicCategory.Plan),[topic])
    
    useFocusEffect(useCallback(()=>{
        //Immediately start ending the session on background when entering this screen.
        if(routeSessionId != null && systemSessionId != null){
            if(routeSessionId == systemSessionId){
                dispatch(endSession(async (success) => {
                    if(success){
                        setCanClose(true)
                    }
                }))
            }else{
                props.navigation.goBack()
            }
        }
    }, [props.navigation, routeSessionId, systemSessionId]))

    const onPressExit = useCallback(()=>{
        props.navigation.popToTop()
    }, [props.navigation])
    
    return <View className="flex-1 items-center my-14">
        <SessionTitleRibbon topic={topic} containerClassName=""/>
        <View className="flex-1 self-stretch items-center justify-center mb-20">
            <Text style={styleTemplates.withBoldFont} className={`text-3xl text-slate-700 mt-20 mb-8`}>{t("Session.EndingMessage")}</Text>
            <View className="flex-row flex-wrap gap-10">
                {
                    numStarsLoopArray.map((_, index) => <Image key={index} source={require('../../../assets/images/feedback-star.png')} className="w-36 h-36"/>)
                }
            </View>
            <TailwindButton onPress={onPressExit} disabled={!canClose} title={t("Session.Menu.GoHome")} containerClassName="min-w-[300px] w-[30vw] mx-16 mt-20" buttonStyleClassName={`${topicColorFG} h-20`} disabledButtonStyleClassName={topicColorDimmed} titleClassName="text-white text-2xl" roundedClassName="rounded-full"/>
        </View>
    </View>
}