import { useFocusEffect } from "@react-navigation/native"
import { useCallback, useEffect, useRef, useState } from "react"
import { BackHandler } from "react-native"

export function usePrevious<T>(value: T): T {
    const currentRef = useRef<T>(value)
    const previousRef = useRef<T>()
    if (currentRef.current !== value) {
        previousRef.current = currentRef.current
        currentRef.current = value
    }
    return previousRef.current
}

export function useDisableBack(){
    
    useFocusEffect(useCallback(()=>{
        const subs = BackHandler.addEventListener('hardwareBackPress', () => {
            console.log("Back prevented.")
            return true
        })

        return () => subs.remove()
    }, []))
}

export function useNonNullUpdatedValue<Result>(value: Result): Result {

    const [safeState, setSafeState] = useState<Result>(value)

    useEffect(()=>{
        if(value != null){
            setSafeState(value)
        }
    }, [value])
    
    return safeState
}