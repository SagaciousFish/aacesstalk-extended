import { HillBackgroundView } from "apps/client-rn/src/components/HillBackgroundView"
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useCallback, useEffect, useMemo, useState } from "react"
import { useTranslation } from "react-i18next"
import { Alert, InteractionManager, Platform, StyleSheet, Text, View } from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import format from 'pupa';
import { TopicButton } from "../components/TopicButton"
import CalendarImage from "../../../assets/images/calendar.svg"
import LogoImage from "../../../assets/images/logo-extended.svg"
import HomeImage from "../../../assets/images/home.svg"
import StarImage from "../../../assets/images/star.svg"
import { ProfileButton } from "../components/ProfileButton"
import { TopicCategory, setSessionInitInfo, startNewSession } from "@aacesstalk/libs/ts-core"
import { NativeStackScreenProps } from "@react-navigation/native-stack"
import { MainRoutes } from "../../../navigation"
import { getTimeZone } from "react-native-localize"
import {checkMultiple, PERMISSIONS, request} from 'react-native-permissions'
import { useFocusEffect } from "@react-navigation/native"
import { fetchSessionInfoSummaries } from "libs/ts-core/src/lib/redux/reducers/dyad-status"
import { checkBackendStatus, useBackendResponsiveCheck } from "../../system-status/reducer"
import { useNonNullUpdatedValue } from "apps/client-rn/src/utils/hooks"

const styles = StyleSheet.create({
    topicFreeDimensions: {right: '5%', bottom: '10%', width: '70%', height: '70%'},
    topicPlanDimensions: {left:20},
    topicRecallDimensions: {right: '16%', bottom: '18%', width: '70%', height: '70%'}
})

const REQUIRED_PERMISSIONS = []
switch(Platform.OS){
    case 'android':
        REQUIRED_PERMISSIONS.push(PERMISSIONS.ANDROID.RECORD_AUDIO)
        break;
    case 'ios':
        REQUIRED_PERMISSIONS.push(PERMISSIONS.IOS.MICROPHONE)
        break;
}

function useSessionCounts(topicCategory: TopicCategory): {today: number, total: number}{
    const counts = useSelector(state => state.dyadStatus.numSessionsByTopicCategory[topicCategory])
    return {
        today: counts?.today || 0,
        total: counts?.total || 0
    }
}

const FreeTopicButton = (props: {style?: any, disabled?: boolean, onPress}) => {

    const {t} = useTranslation()

    const child_name = useNonNullUpdatedValue(useSelector(state => state.auth.dyadInfo?.child_name))

    const sessionCounts = useSessionCounts(TopicCategory.Free)
    
    const label = useMemo(()=>{
        return format(t("TopicSelection.FreeTemplate"), {child_name}, {ignoreMissing: true})
    }, [child_name, t])

    return <TopicButton style={props.style} disabled={props.disabled} title={label} buttonClassName="bg-topicfree-fg" 
                imageComponent={<StarImage/>}
                imageContainerStyleDimensions={styles.topicFreeDimensions}
                imageNormalDegree={-8}
                imagePressedDegree={20}
                numSessionsToday={sessionCounts.today}
                numSessionsTotal={sessionCounts.total}
                onPress={props.onPress}
                />
}

const PlanTopicButton = (props: {style?: any, disabled?: boolean, onPress}) => {

    const {t} = useTranslation()

    const sessionCounts = useSessionCounts(TopicCategory.Plan)

    return <TopicButton style={props.style} disabled={props.disabled} title={t("TopicSelection.Plan")} buttonClassName="bg-topicplan-fg" imageComponent={<CalendarImage/>} 
    imageContainerStyleDimensions={styles.topicPlanDimensions} imageNormalDegree={10} imagePressedDegree={-20} onPress={props.onPress}
    numSessionsToday={sessionCounts.today}
    numSessionsTotal={sessionCounts.total}
    />
}

const RecallTopicButton = (props: {style?: any, disabled?: boolean, onPress}) => {


    const {t} = useTranslation()

    const sessionCounts = useSessionCounts(TopicCategory.Recall)

    return <TopicButton style={props.style} disabled={props.disabled} title={t("TopicSelection.Recall")} buttonClassName="bg-topicrecall-fg" imageComponent={<HomeImage/>} 
    imageContainerStyleDimensions={styles.topicRecallDimensions} 
    imageNormalDegree={-8} imagePressedDegree={20} onPress={props.onPress} numSessionsToday={sessionCounts.today}
    numSessionsTotal={sessionCounts.total}/>
}

const BackendConnectionCheckerOverlay = () => {
    const dispatch = useDispatch()
    const isServerResponsive = useSelector(state => state.systemStatus.isServerResponsive)
    
    const onPressRefresh = useCallback(()=>{
        dispatch(checkBackendStatus())
    }, [])

    const [t] = useTranslation()
    
    return isServerResponsive ? null : <View className="absolute top-0 left-0 right-0 bottom-0 bg-white/40 items-center justify-center">
        <View className="max-w-[40vw] bg-white p-3 px-6 rounded-xl shadow-lg border-red-400 border-4">
            <Text style={styleTemplates.withBoldFont} className="text-lg">{t("ERRORS.NETWORK_CONNECTION")}</Text>
            <TailwindButton title={t('ERRORS.NETWORK_CONNECTION_REFRESH')} onPress={onPressRefresh}/>
        </View>
        </View>
}

export const HomeScreen = (props: NativeStackScreenProps<MainRoutes.MainNavigatorParamList, "home">) => {

    useBackendResponsiveCheck()

    const [permissionsGranted, setPermissionsGranted] = useState(false)

    const {t} = useTranslation()

    const dispatch = useDispatch()

    const onPressPlanButton = useCallback(async ()=>{
        dispatch(checkBackendStatus((isResponsive) => {
            if(isResponsive){
                const topic = { category: TopicCategory.Plan }
                dispatch(startNewSession(topic, getTimeZone()))
                props.navigation.navigate(MainRoutes.ROUTE_SESSION, { topic })
            }
        }))
    }, [])

    const onPressRecallButton = useCallback(async ()=>{
        dispatch(checkBackendStatus((isResponsive) => {
            if(isResponsive){
                const topic = { category: TopicCategory.Recall }
                dispatch(setSessionInitInfo({topic}))
                dispatch(startNewSession(topic, getTimeZone()))
                requestAnimationFrame(()=>{
                    props.navigation.navigate(MainRoutes.ROUTE_SESSION, { topic })
                })
            }
        }))
    }, [])

    const onPressFreeTopicButton = useCallback(async ()=>{
        dispatch(checkBackendStatus((isResponsive) => {
            if(isResponsive){
                requestAnimationFrame(()=>{
                    props.navigation.navigate(MainRoutes.ROUTE_FREE_TOPIC_SELECTION)
                })
            }
        }))
    }, [])

    const onPressStarsButton = useCallback(()=>{
        props.navigation.navigate('stars')
    }, [props.navigation])

    const checkPermissionsGranted = useCallback(async () => {
        if(REQUIRED_PERMISSIONS.length > 0){
            const permissionStatuses = await checkMultiple(REQUIRED_PERMISSIONS)
            const isAllGranted = REQUIRED_PERMISSIONS.map(p => permissionStatuses[p]).findIndex(s => s != 'granted') === -1
            setPermissionsGranted(isAllGranted)
            return isAllGranted
        }else{
            setPermissionsGranted(true)
            return true
        }
    }, [])

    const handlePermission = useCallback(async ()=>{
        const isGranted = await checkPermissionsGranted()
        if(isGranted){
            setPermissionsGranted(true)
        }else{
            if(REQUIRED_PERMISSIONS.length > 0){
                let isGranted = false
                const permissionStatuses = await checkMultiple(REQUIRED_PERMISSIONS)
                for(const permission of REQUIRED_PERMISSIONS){
                    console.log(permission, permissionStatuses[permission])
                    if(permissionStatuses[permission] == 'denied'){
                        console.log("request permission.")
                        await request(permission)
                    }
                }
                isGranted = await checkPermissionsGranted()
                if(!isGranted){
                    Alert.alert("Permissions", "The app may not work as intended as you did not approve all required permissions. Please approve them all in the app settings manually.")
                }
            }
        }
    }, [checkPermissionsGranted])

    useEffect(()=>{
        handlePermission().then()
    }, [])

    const fetchSessionSummaries = useCallback(()=>{
        dispatch(fetchSessionInfoSummaries())
    }, [])

    useFocusEffect(fetchSessionSummaries)

    const isServerResponsive = useSelector(state => state.systemStatus.isServerResponsive)

    useEffect(()=>{
        if(isServerResponsive === true){
            // Server was connected.
            fetchSessionSummaries()
        }
    }, [isServerResponsive, fetchSessionSummaries])

    return <HillBackgroundView containerClassName="items-center justify-center">
        <SafeAreaView className="flex-1 self-stretch items-center justify-center">
            <LogoImage width={200} height={80}/>
            <Text className="text-3xl text-slate-800 text-center" style={styleTemplates.withBoldFont}>{t("TopicSelection.Title")}</Text>
            <View className="flex-row gap-x-12 mt-24 mb-20">
               
                <PlanTopicButton disabled={!permissionsGranted} onPress={onPressPlanButton}/>
                <RecallTopicButton disabled={!permissionsGranted} onPress={onPressRecallButton}/>
                <FreeTopicButton disabled={!permissionsGranted} onPress={onPressFreeTopicButton}/>
            </View>
            <ProfileButton/>
            <TailwindButton containerClassName="absolute right-5 bottom-5" buttonStyleClassName="py-5 px-12" roundedClassName="rounded-full" 
                title={t("TopicSelection.StarCount")} onPress={onPressStarsButton}/>
        </SafeAreaView>       
        <BackendConnectionCheckerOverlay/> 
        </HillBackgroundView>
}