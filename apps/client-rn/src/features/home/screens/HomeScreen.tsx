import { HillBackgroundView } from "apps/client-rn/src/components/HillBackgroundView"
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components"
import { useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Text, View } from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import format from 'string-template';
import { TopicButton } from "../components/TopicButton"
import CalendarImage from "../../../assets/images/calendar.svg"
import LogoImage from "../../../assets/images/logo-extended.svg"
import HomeImage from "../../../assets/images/home.svg"
import StarImage from "../../../assets/images/star.svg"
import { ProfileButton } from "../components/ProfileButton"

const FreeTopicButton = (props: {style?: any}) => {

    const {t} = useTranslation()

    const child_name = useSelector(state => state.auth.dyadInfo?.child_name)
    
    const label = useMemo(()=>{
        return format(t("TopicSelection.FreeTemplate"), {child_name})
    }, [child_name])

    return <TopicButton style={props.style} title={label} dialogueCount={0} buttonClassName="bg-topicfree" 
                imageComponent={<StarImage/>}
                imageContainerStyleDimensions={{right: '5%', bottom: '10%', width: '70%', height: '70%'}}
                imageNormalDegree={-8}
                imagePressedDegree={20}
                />
}

export const HomeScreen = () => {

    const {t} = useTranslation()

    return <HillBackgroundView containerClassName="items-center justify-center">
        <SafeAreaView className="flex-1 self-stretch items-center justify-center">
            <LogoImage width={200} height={80}/>
            <Text className="text-3xl text-slate-800 text-center" style={styleTemplates.withBoldFont}>{t("TopicSelection.Title")}</Text>
            <View className="flex-row space-x-12 mt-24 mb-20">
                <TopicButton title={t("TopicSelection.Plan")} dialogueCount={0} buttonClassName="bg-topicplan" imageComponent={<CalendarImage/>} 
                    imageContainerStyleDimensions={{left:20}} imageNormalDegree={10} imagePressedDegree={-20}/>
                <TopicButton title={t("TopicSelection.Recall")} dialogueCount={0} buttonClassName="bg-topicrecall" imageComponent={<HomeImage/>} 
                    imageContainerStyleDimensions={{right: '16%', bottom: '18%', width: '70%', height: '70%'}} 
                    imageNormalDegree={-8} imagePressedDegree={20}/>
                <FreeTopicButton/>
            </View>
            <ProfileButton/>
            <TailwindButton containerClassName="absolute right-5 bottom-5" buttonStyleClassName="py-5 px-12" roundedClassName="rounded-full" title={t("TopicSelection.StarCount")}></TailwindButton>
        </SafeAreaView>
        </HillBackgroundView>
}