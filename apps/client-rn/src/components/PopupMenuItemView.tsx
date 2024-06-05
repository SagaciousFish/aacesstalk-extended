import { Text } from "react-native"
import { TailwindButton } from "./tailwind-components"
import { MenuIcon } from "./vector-icons"
import { styleTemplates } from "../styles"

export const PopupMenuItemView = (props: {
    title: string,
    showBorder?: boolean,
    destructive?: boolean,
    onPress?: () => void
}) => {
    return <TailwindButton onPress={props.onPress} buttonStyleClassName="flex-row items-center justify-between py-5" containerClassName={`${props.showBorder !== false ? "border-t-2" : "border-none"} border-slate-200`}>
        <Text style={styleTemplates.withBoldFont} className={`text-lg ${props.destructive === true ? 'text-red-400' : ""}`}>{props.title}</Text>
    </TailwindButton>
}