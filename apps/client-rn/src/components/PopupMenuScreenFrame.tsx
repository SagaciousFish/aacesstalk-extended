import { TailwindButton } from "apps/client-rn/src/components/tailwind-components";
import { ExIcon } from "apps/client-rn/src/components/vector-icons";
import { View, Pressable } from "react-native";
import Reanimated, { Easing, SlideInDown } from 'react-native-reanimated';

export const PopupMenuScreenFrame = (props: {
    onPop: ()=>void,
    panelClassName?: string
    backgroundClassName?: string,
    dismissOnPressOutside?: boolean,
    children?: any
}) => {
    
    return <View className={`relative flex-1 items-center justify-end bg-slate-800/30 ${props.backgroundClassName}`}>
        {
            props.dismissOnPressOutside !== false ? <Pressable accessible={false} className="absolute left-0 right-0 top-0 bottom-0" onPress={props.onPop}/> : null
        }
        <Reanimated.View entering={SlideInDown.duration(400).easing(Easing.out(Easing.cubic))}
            id={"frame"} className={`bg-white max-w-[50vw] min-w-[30vw] px-1 pt-1 rounded-t-2xl ${props.panelClassName}`}>
            <TailwindButton onPress={props.onPop} containerClassName="self-end mb-1" buttonStyleClassName="p-2" roundedClassName="rounded-full" shadowClassName="shadow-none"><ExIcon width={32} height={32} fill={"#575757"}/></TailwindButton>
            {
                props.children
            }
        </Reanimated.View>
        </View>
}