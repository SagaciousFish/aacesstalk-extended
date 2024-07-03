import { HillBackgroundView } from "apps/client-rn/src/components/HillBackgroundView"
import { TailwindButton } from "apps/client-rn/src/components/tailwind-components"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { styleTemplates } from "apps/client-rn/src/styles"
import { useCallback, useEffect, useMemo, useState } from "react"
import { useTranslation } from "react-i18next"
import { Alert, InteractionManager, Platform, StyleSheet, Text, View } from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import format from 'string-template';
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
import {check, checkMultiple, PERMISSIONS, PermissionStatus, request} from 'react-native-permissions'
import NetInfo, { useNetInfo, useNetInfoInstance } from "@react-native-community/netinfo"

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

const FreeTopicButton = (props: {style?: any, disabled?: boolean}) => {

    const {t} = useTranslation()

    const child_name = useSelector(state => state.auth.dyadInfo?.child_name)
    
    const label = useMemo(()=>{
        return format(t("TopicSelection.FreeTemplate"), {child_name})
    }, [child_name])

    return <TopicButton style={props.style} disabled={props.disabled} title={label} dialogueCount={0} buttonClassName="bg-topicfree-fg" 
                imageComponent={<StarImage/>}
                imageContainerStyleDimensions={styles.topicFreeDimensions}
                imageNormalDegree={-8}
                imagePressedDegree={20}
                />
}

const BackendConnectionCheckerOverlay = () => {
    const netInfo = useNetInfo()
    console.log(netInfo)
    
    const onPressRefresh = useCallback(()=>{
        InteractionManager.runAfterInteractions(async ()=>{
            console.log("Refresh connection")
            await NetInfo.refresh()
        })
    }, [])

    const [t] = useTranslation()
    
    return netInfo.isInternetReachable ? null : <View className="absolute top-0 left-0 right-0 bottom-0 bg-white/40 items-center justify-center">
        <View className="max-w-[40vw] bg-white p-3 px-6 rounded-xl shadow-lg border-red-400 border-4">
            <Text style={styleTemplates.withBoldFont} className="text-lg">{t("ERRORS.NETWORK_CONNECTION")}</Text>
            <TailwindButton title={t('ERRORS.NETWORK_CONNECTION_REFRESH')} onPress={onPressRefresh}/>
        </View>
        </View>
}

export const HomeScreen = (props: NativeStackScreenProps<MainRoutes.MainNavigatorParamList, "home">) => {

    const [permissionsGranted, setPermissionsGranted] = useState(false)

    const {t} = useTranslation()

    const dispatch = useDispatch()

    const checkBackendConnection = useCallback(async ()=>{
        const netInfo = await NetInfo.refresh()
    }, [])

    const onPressPlanButton = useCallback(async ()=>{
        await checkBackendConnection()
        requestAnimationFrame(async ()=>{
            const netInfo = await NetInfo.fetch()
            if(netInfo.isInternetReachable){
                const topic = { category: TopicCategory.Plan }
                dispatch(startNewSession(topic, getTimeZone()))
                props.navigation.navigate(MainRoutes.ROUTE_SESSION, { topic })
            }
        })
        
    }, [checkBackendConnection])

    const onPressRecallButton = useCallback(async ()=>{
        await checkBackendConnection()
        requestAnimationFrame(async ()=>{
            const netInfo = await NetInfo.fetch()
            if(netInfo.isInternetReachable){
                const topic = { category: TopicCategory.Recall }
                dispatch(setSessionInitInfo({topic}))
                dispatch(startNewSession(topic, getTimeZone()))
                requestAnimationFrame(()=>{
                    props.navigation.navigate(MainRoutes.ROUTE_SESSION, { topic })
                })
            }
        })
    }, [checkBackendConnection])

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

    return <HillBackgroundView containerClassName="items-center justify-center">
        <SafeAreaView className="flex-1 self-stretch items-center justify-center">
            <LogoImage width={200} height={80}/>
            <Text className="text-3xl text-slate-800 text-center" style={styleTemplates.withBoldFont}>{t("TopicSelection.Title")}</Text>
            <View className="flex-row space-x-12 mt-24 mb-20">
                <TopicButton disabled={!permissionsGranted} title={t("TopicSelection.Plan")} dialogueCount={0} buttonClassName="bg-topicplan-fg" imageComponent={<CalendarImage/>} 
                    imageContainerStyleDimensions={styles.topicPlanDimensions} imageNormalDegree={10} imagePressedDegree={-20} onPress={onPressPlanButton}/>
                <TopicButton disabled={!permissionsGranted} title={t("TopicSelection.Recall")} dialogueCount={0} buttonClassName="bg-topicrecall-fg" imageComponent={<HomeImage/>} 
                    imageContainerStyleDimensions={styles.topicRecallDimensions} 
                    imageNormalDegree={-8} imagePressedDegree={20} onPress={onPressRecallButton}/>
                <FreeTopicButton disabled={!permissionsGranted}/>
            </View>
            <ProfileButton/>
            <TailwindButton containerClassName="absolute right-5 bottom-5" buttonStyleClassName="py-5 px-12" roundedClassName="rounded-full" title={t("TopicSelection.StarCount")}/>
        </SafeAreaView>       
        <BackendConnectionCheckerOverlay/> 
        </HillBackgroundView>
}