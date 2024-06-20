import { endSession } from "@aacesstalk/libs/ts-core"
import { useFocusEffect } from "@react-navigation/native"
import { NativeStackScreenProps } from "@react-navigation/native-stack"
import { MainRoutes } from "apps/client-rn/src/navigation"
import { useDispatch, useSelector } from "apps/client-rn/src/redux/hooks"
import { useCallback, useState } from "react"
import { View } from "react-native"

export const SessionClosingScreen = (props: NativeStackScreenProps<MainRoutes.MainNavigatorParamList, "session-closing">) => {
    
    const systemSessionId = useSelector(state => state.session.id)
    const dispatch = useDispatch()

    const [canClose, setCanClose] = useState(false)
    
    useFocusEffect(useCallback(()=>{
        //Immediately start ending the session on background when entering this screen.
        if(props.route.params.sessionId == systemSessionId){
            dispatch(endSession(async (success) => {
                if(success){
                    setCanClose(true)
                }
            }))
        }else{
            props.navigation.goBack()
        }
    }, [props.navigation, props.route.params.sessionId, systemSessionId]))
    
    return <View>
        
    </View>
}