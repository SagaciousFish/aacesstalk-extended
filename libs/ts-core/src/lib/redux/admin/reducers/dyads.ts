import { PayloadAction, createEntityAdapter, createSlice } from "@reduxjs/toolkit"
import { DyadWithPasscode } from "../../../model-types"
import { AdminCoreState, AdminCoreThunk } from "../store"
import { Http } from "../../../net/http"

const dyadEntityAdapter = createEntityAdapter<DyadWithPasscode>()
const INITIAL_DYAD_ENTITY_STATE = dyadEntityAdapter.getInitialState()

export interface DyadsState{
    dyadsEntityState: typeof INITIAL_DYAD_ENTITY_STATE,
    isLoadingDyadList: boolean,
    isCreatingDyad: boolean
}

const INITIAL_DYADS_STATE: DyadsState = {
    dyadsEntityState: INITIAL_DYAD_ENTITY_STATE,
    isLoadingDyadList: false,
    isCreatingDyad: false
}

const dyadsSlice = createSlice({
    name: "dyads",
    initialState: INITIAL_DYADS_STATE, 
    reducers: {
        _initialize: () => INITIAL_DYADS_STATE,
        _setLoadingDyadsFlag: (state, action: PayloadAction<boolean>) => {
            state.isLoadingDyadList = action.payload
        },
        _setCreatingDyadFlag: (state, action: PayloadAction<boolean>) => {
            state.isCreatingDyad = action.payload
        },
        _setLoadedDyads: (state, action: PayloadAction<Array<DyadWithPasscode>>) => {
            dyadEntityAdapter.setAll(state.dyadsEntityState, action.payload)
        },
        _removeDyadById: (state, action: PayloadAction<string>) => {
            dyadEntityAdapter.removeOne(state.dyadsEntityState, action.payload)
        },
        _appendDyad: (state, action: PayloadAction<DyadWithPasscode>) => {
            dyadEntityAdapter.addOne(state.dyadsEntityState, action.payload)
        }
    }
})

export const dyadsSelectors = dyadEntityAdapter.getSelectors((state: AdminCoreState) => state.dyads.dyadsEntityState)

export function loadDyads(): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if(state.auth.jwt != null){
            dispatch(dyadsSlice.actions._setLoadingDyadsFlag(true))
            try{
                const resp = await Http.axios.get(Http.ENDPOINT_ADMIN_DYADS_ALL, {
                    headers: await Http.getSignedInHeaders(state.auth.jwt!)
                })

                const {dyads} = resp.data
                dispatch(dyadsSlice.actions._setLoadedDyads(dyads))

            }catch(ex){
                console.log(ex)
            }finally{
                dispatch(dyadsSlice.actions._setLoadingDyadsFlag(false))
            }
        }
    }
}

export function createDyad(info: any, onCreated: (dyad: DyadWithPasscode) => void, onError: (error: any) => void): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if(state.auth.jwt != null){
            dispatch(dyadsSlice.actions._setCreatingDyadFlag(true))

            try{
                const resp = await Http.axios.post(Http.ENDPOINT_ADMIN_DYADS_NEW, info, {
                    headers: await Http.getSignedInHeaders(state.auth.jwt)
                })
                dispatch(dyadsSlice.actions._appendDyad(resp.data))
                onCreated(resp.data)
            }catch(ex){
                console.log(ex)
                onError(ex)
            }finally {
                dispatch(dyadsSlice.actions._setCreatingDyadFlag(false))
            }
        }
    }
}

export default dyadsSlice.reducer
