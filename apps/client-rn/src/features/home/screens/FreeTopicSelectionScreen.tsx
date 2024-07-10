import { Http, TopicCategory, freeTopicDetailSelectors, setSessionInitInfo, startNewSession } from "@aacesstalk/libs/ts-core";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { PopupMenuScreenFrame } from "apps/client-rn/src/components/PopupMenuScreenFrame";
import { MainRoutes } from "apps/client-rn/src/navigation";
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks";
import { useCallback, useEffect, useState } from "react";
import { Text, View, StyleSheet, Pressable } from "react-native";
import { SessionTitleRibbon } from "../../session/components/SessionTitleRibbon";
import { getTopicColorClassNames, styleTemplates } from "apps/client-rn/src/styles";
import { useTranslation } from "react-i18next";
import { FasterImageView, ImageOptions } from "@candlefinance/faster-image";
import Reanimated, { Easing, interpolate, useAnimatedStyle, useSharedValue, withSpring, withTiming } from 'react-native-reanimated'
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useNavigation } from "@react-navigation/core";
import { checkBackendStatus } from "../../system-status/reducer";
import { getTimeZone } from "react-native-localize";

const styles = StyleSheet.create({
    imageView: {aspectRatio: 1, marginBottom: 12, width: '100%'}
})

const FreeTopicDetailCard = (props: {id: string, style?: any}) => {

    const navigation = useNavigation<NativeStackNavigationProp<MainRoutes.MainNavigatorParamList, "free-topic-selection">>()

    const detailInfo = useSelector(state => freeTopicDetailSelectors.selectById(state, props.id))

    const pressAnimProgress = useSharedValue(0)

    const onPressIn = useCallback(()=>{
        pressAnimProgress.value = withTiming(1, {duration: 200, easing: Easing.out(Easing.cubic)})
    }, [])

    const onPressOut = useCallback(()=>{
        pressAnimProgress.value = withSpring(0, {duration: 500})
    }, [])

    const dispatch = useDispatch()

    const onPress = useCallback(()=>{

        dispatch(checkBackendStatus((isResponsive) => {
            if(isResponsive){
                const topic = {
                    category: TopicCategory.Free,
                    subtopic: detailInfo.subtopic,
                    subdescription: detailInfo.subtopic_description
                }
                dispatch(setSessionInitInfo({topic}))
                dispatch(startNewSession(topic, getTimeZone()))
                requestAnimationFrame(()=>{
                    navigation.replace('session', {topic})
                })
            }
        }))

    }, [detailInfo, navigation])

    const containerAnimStyle = useAnimatedStyle(() => {
        return {
            transform: [
                {scale: interpolate(pressAnimProgress.value, [0, 1], [1, 0.95])},
                {translateY: interpolate(pressAnimProgress.value, [0, 1], [0, 10])}
        ] as any
        }
    }, [])

    const token = useSelector(state => state.auth.jwt)

    const [imageSource, setImageSource] = useState<ImageOptions>(undefined)

    const applyCardImage = useCallback(async () => {
        const headers = await Http.getSignedInHeaders(token)

        setImageSource({
            headers,
            url: Http.axios.defaults.baseURL + Http.ENDPOINT_DYAD_MEDIA_FREE_TOPIC_IMAGE + "?detail_id=" + props.id,
        } as ImageOptions)
    }, [token, props.id])

    useEffect(()=>{
        applyCardImage().then()
    }, [applyCardImage])

    return <Pressable accessible={false} style={props.style} onPressIn={onPressIn} onPressOut={onPressOut} onPress={onPress}>
        <Reanimated.View style={containerAnimStyle} className="bg-white w-[13.5vw] rounded-2xl p-0 border-orange-400 border-[3px] shadow-lg shadow-black overflow-hidden">
            <FasterImageView style={styles.imageView} source={imageSource}/>
            <Text style={styleTemplates.withExtraboldFont} className="text-xl text-center text-slate-700" numberOfLines={2}>{detailInfo?.subtopic}</Text>
        </Reanimated.View>
    </Pressable>
}

export const FreeTopicSelectionScreen = (props: NativeStackScreenProps<MainRoutes.MainNavigatorParamList, "free-topic-selection">) => {

    const [t] = useTranslation()

    const onPop = useCallback(()=>{
        props.navigation.popToTop()
    },[props.navigation])

    const topicDetailIds = useSelector(freeTopicDetailSelectors.selectIds)

    return <PopupMenuScreenFrame dismissOnPressOutside onPop={onPop} backgroundClassName="justify-center p-8" panelClassName={`bg-topicfree-bg pb-8 pt-3 px-3 rounded-3xl w-full max-w-full`}>
        <SessionTitleRibbon category={TopicCategory.Free} containerClassName="self-center"/>
        <Text style={styleTemplates.withBoldFont} className="text-2xl text-black text-center mt-6 mb-0">{t("Session.FreeTopicSelectCard")}</Text>
        <View className="flex-row flex-wrap gap-3 m-2">
        {
            topicDetailIds.map(id => <FreeTopicDetailCard id={id} key={id}/>)
        }
        </View>
    </PopupMenuScreenFrame>
}