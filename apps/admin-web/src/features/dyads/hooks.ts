import { useMatch } from "react-router-dom"

export function useDyadId(): string | undefined {
    const urlMatch = useMatch("/dyads/:dyadId/*")
    return urlMatch?.params.dyadId
}