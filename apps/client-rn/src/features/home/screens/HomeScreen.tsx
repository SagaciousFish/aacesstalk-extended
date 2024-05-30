import { signOutDyadThunk } from "@aacesstalk/libs/ts-core"
import { HillBackgroundView } from "apps/client-rn/src/components/HillBackgroundView"
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { forwardRef, useCallback, useEffect, useMemo, useRef } from "react"
import { useTranslation } from "react-i18next"
import { Alert, Text, View } from "react-native"
import { Gesture, GestureDetector, TapGesture } from "react-native-gesture-handler"
import { SafeAreaView } from "react-native-safe-area-context"
import format from 'string-template';
import { TopicButton } from "../components/TopicButton"
import CalendarImage from "../../../assets/images/calendar.svg"
import HomeImage from "../../../assets/images/home.svg"
import StarImage from "../../../assets/images/star.svg"
import { ProfileButton } from "../components/ProfileButton"

const FreeTopicButton = (props: {style?: any}) => {

    const {t} = useTranslation()

    const child_name = useSelector(state => state.auth.dyadInfo?.child_name)
    
    const label = useMemo(()=>{
        return format(t("TopicSelection.FreeTemplate"), {child_name})
    }, [child_name])

    return <TopicButton style={props.style} title={label} dialogueCount={0} buttonClassName="bg-topicfree" imageComponent={<StarImage/>}/>
}

export const HomeScreen = () => {

    const {t} = useTranslation()

    return <HillBackgroundView containerClassName="items-center justify-center">
        <SafeAreaView className="flex-1 self-stretch items-center justify-center">
            <Text className="text-3xl text-slate-800 text-center" style={styleTemplates.withBoldFont}>{t("TopicSelection.Title")}</Text>
            <View className="flex-row space-x-12 mt-24 mb-10">
                <TopicButton title={t("TopicSelection.Plan")} dialogueCount={0} buttonClassName="bg-topicplan" imageComponent={<CalendarImage/>}/>
                <TopicButton title={t("TopicSelection.Recall")} dialogueCount={0} buttonClassName="bg-topicrecall" imageComponent={<HomeImage/>}/>
                <FreeTopicButton/>
            </View>
            <ProfileButton/>
            <TailwindButton containerClassName="absolute right-5 bottom-5" buttonStyleClassName="py-5 px-12" roundedClassName="rounded-full" title={t("TopicSelection.StarCount")}></TailwindButton>
        </SafeAreaView>
        </HillBackgroundView>
}