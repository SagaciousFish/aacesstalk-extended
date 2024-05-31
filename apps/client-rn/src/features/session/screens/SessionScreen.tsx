import { NativeStackScreenProps } from '@react-navigation/native-stack'
import { MainRoutes } from 'apps/client-rn/src/navigation'
import { View, Text } from 'react-native'

export const SessionScreen = (props: NativeStackScreenProps<MainRoutes.MainNavigatorParamList, "session">) => {

    console.log(props.route.params.topic)

    return <View className="flex-1"><Text>Session Screen</Text></View>
}