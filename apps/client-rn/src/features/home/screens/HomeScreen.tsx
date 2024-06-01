import { HillBackgroundView } from "apps/client-rn/src/components/HillBackgroundView"
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useCallback, useMemo } from "react"
import { useTranslation } from "react-i18next"
import { StyleSheet, Text, View } from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import format from 'string-template';
import { TopicButton } from "../components/TopicButton"
import CalendarImage from "../../../assets/images/calendar.svg"
import LogoImage from "../../../assets/images/logo-extended.svg"
import HomeImage from "../../../assets/images/home.svg"
import StarImage from "../../../assets/images/star.svg"
import { ProfileButton } from "../components/ProfileButton"
import { TopicCategory, startNewSession } from "@aacesstalk/libs/ts-core"
import { NativeStackScreenProps } from "@react-navigation/native-stack"
import { MainRoutes } from "../../../navigation"
import { getTimeZone } from "react-native-localize"

const styles = StyleSheet.create({
    topicFreeDimensions: {right: '5%', bottom: '10%', width: '70%', height: '70%'},
    topicPlanDimensions: {left:20},
    topicRecallDimensions: {right: '16%', bottom: '18%', width: '70%', height: '70%'}
})

const FreeTopicButton = (props: {style?: any}) => {

    const {t} = useTranslation()

    const child_name = useSelector(state => state.auth.dyadInfo?.child_name)
    
    const label = useMemo(()=>{
        return format(t("TopicSelection.FreeTemplate"), {child_name})
    }, [child_name])

    return <TopicButton style={props.style} title={label} dialogueCount={0} buttonClassName="bg-topicfree-fg" 
                imageComponent={<StarImage/>}
                imageContainerStyleDimensions={styles.topicFreeDimensions}
                imageNormalDegree={-8}
                imagePressedDegree={20}
                />
}

export const HomeScreen = (props: NativeStackScreenProps<MainRoutes.MainNavigatorParamList, "home">) => {

    const {t} = useTranslation()

    const dispatch = useDispatch()

    const onPressPlanButton = useCallback(()=>{
        const topic = { category: TopicCategory.Plan }
        dispatch(startNewSession(topic, getTimeZone()))
        props.navigation.navigate(MainRoutes.ROUTE_SESSION, { topic })
    }, [])

    const onPressRecallButton = useCallback(()=>{
        const topic = { category: TopicCategory.Recall }
        dispatch(startNewSession({ category: TopicCategory.Plan }, getTimeZone()))
        props.navigation.navigate(MainRoutes.ROUTE_SESSION, { topic })
    }, [])

    return <HillBackgroundView containerClassName="items-center justify-center">
        <SafeAreaView className="flex-1 self-stretch items-center justify-center">
            <LogoImage width={200} height={80}/>
            <Text className="text-3xl text-slate-800 text-center" style={styleTemplates.withBoldFont}>{t("TopicSelection.Title")}</Text>
            <View className="flex-row space-x-12 mt-24 mb-20">
                <TopicButton title={t("TopicSelection.Plan")} dialogueCount={0} buttonClassName="bg-topicplan-fg" imageComponent={<CalendarImage/>} 
                    imageContainerStyleDimensions={styles.topicPlanDimensions} imageNormalDegree={10} imagePressedDegree={-20} onPress={onPressPlanButton}/>
                <TopicButton title={t("TopicSelection.Recall")} dialogueCount={0} buttonClassName="bg-topicrecall-fg" imageComponent={<HomeImage/>} 
                    imageContainerStyleDimensions={styles.topicRecallDimensions} 
                    imageNormalDegree={-8} imagePressedDegree={20} onPress={onPressRecallButton}/>
                <FreeTopicButton/>
            </View>
            <ProfileButton/>
            <TailwindButton containerClassName="absolute right-5 bottom-5" buttonStyleClassName="py-5 px-12" roundedClassName="rounded-full" title={t("TopicSelection.StarCount")}></TailwindButton>
        </SafeAreaView>
        </HillBackgroundView>
}