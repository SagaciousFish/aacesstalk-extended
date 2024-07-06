import { PayloadAction, createSlice } from "@reduxjs/toolkit"
import { ClientThunk } from "../../redux/store"
import { Http } from "@aacesstalk/libs/ts-core"
import { useDispatch } from "../../redux/hooks"
import { useEffect } from "react"

export interface SystemStatusState{
    isServerResponsive?: boolean
    checkingBackendStatus: boolean
}

const INITIAL_STATE: SystemStatusState = {
    isServerResponsive: undefined,
    checkingBackendStatus: false
}

const systemStatusSlice = createSlice({
    name: "system-status",
    initialState: INITIAL_STATE,
    reducers: {
        setServerStatus: (state, action: PayloadAction<boolean>) => {
            state.isServerResponsive = action.payload
        },

        setCheckingBackendStatusFlag: (state, action: PayloadAction<boolean>) => {
            state.checkingBackendStatus = action.payload
        }
    }
})

export default systemStatusSlice.reducer

export function checkBackendStatus(onChecked?: (isResponsive: boolean) => void): ClientThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if(state.systemStatus.checkingBackendStatus !== true){
            try {
                dispatch(systemStatusSlice.actions.setCheckingBackendStatusFlag(true))
                const resp = await Http.axios.head(Http.ENDPOINT_PING)
                dispatch(systemStatusSlice.actions.setServerStatus(resp.status === 204))
                onChecked?.(true)
            }catch(ex){
                dispatch(systemStatusSlice.actions.setServerStatus(false))
                onChecked?.(false)
            }finally{
                dispatch(systemStatusSlice.actions.setCheckingBackendStatusFlag(false))
            }
        }
    }
}

export function useBackendResponsiveCheck(){
    const dispatch = useDispatch()

    useEffect(()=>{
        let isMounted = true;

        dispatch(checkBackendStatus())

        const intervalId = setInterval(()=>{
            if(isMounted){
                dispatch(checkBackendStatus())
            }
        }, 5000)

        return () => {
            isMounted = false
            clearInterval(intervalId)
        }
    }, [])
}