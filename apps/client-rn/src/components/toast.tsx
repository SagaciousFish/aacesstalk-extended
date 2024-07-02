import { View, Text } from "react-native"
import {ToastConfig} from 'react-native-toast-message';
import { styleTemplates } from "../styles";

export const toastConfig: ToastConfig = {
    warning: ({text1, props}) => {
        return <View className="max-w-[40vw] p-6 py-3 bg-white border-red-400 border-4 rounded-xl shadow-lg shadow-black">
                <Text style={styleTemplates.withBoldFont} className="text-xl text-center">{text1}</Text>
            </View>
    }
}