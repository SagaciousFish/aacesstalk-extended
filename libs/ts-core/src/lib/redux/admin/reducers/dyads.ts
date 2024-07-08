import { PayloadAction, createEntityAdapter, createSlice } from "@reduxjs/toolkit"
import { DyadWithPasscode, FreeTopicDetail } from "../../../model-types"
import { AdminCoreState, AdminCoreThunk } from "../store"
import { Http } from "../../../net/http"

const dyadEntityAdapter = createEntityAdapter<DyadWithPasscode>()
const INITIAL_DYAD_ENTITY_STATE = dyadEntityAdapter.getInitialState()

const freeTopicDetailEntityAdapter = createEntityAdapter<FreeTopicDetail>()
const INITIAL_FREE_TOPIC_DETAIL_ENTITY_STATE = freeTopicDetailEntityAdapter.getInitialState()

export interface DyadsState{
    dyadsEntityState: typeof INITIAL_DYAD_ENTITY_STATE,
    freeTopicDetailsEntityState: typeof INITIAL_FREE_TOPIC_DETAIL_ENTITY_STATE,
    isLoadingFreeTopics: boolean,
    isLoadingDyadList: boolean,
    isUpdatingFreeTopic: boolean,
    isCreatingDyad: boolean,
    mountedDyadId: string | undefined
}

const INITIAL_DYADS_STATE: DyadsState = {
    dyadsEntityState: INITIAL_DYAD_ENTITY_STATE,
    freeTopicDetailsEntityState: INITIAL_FREE_TOPIC_DETAIL_ENTITY_STATE,
    isLoadingFreeTopics: false,
    isLoadingDyadList: false,
    isCreatingDyad: false,
    isUpdatingFreeTopic: false,
    mountedDyadId: undefined
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
        _setLoadingFreeTopicsFlag: (state, action: PayloadAction<boolean>) => {
            state.isLoadingFreeTopics = action.payload
        },
        _setUpdatingFreeTopicsFlag: (state, action: PayloadAction<boolean>) => {
            state.isUpdatingFreeTopic = action.payload
        },
        _setLoadedDyads: (state, action: PayloadAction<Array<DyadWithPasscode>>) => {
            dyadEntityAdapter.setAll(state.dyadsEntityState, action.payload)
        },
        _setOneDyad: (state, action: PayloadAction<DyadWithPasscode>) => {
            dyadEntityAdapter.setOne(state.dyadsEntityState, action.payload)
        },
        _removeDyadById: (state, action: PayloadAction<string>) => {
            dyadEntityAdapter.removeOne(state.dyadsEntityState, action.payload)
        },
        _appendDyad: (state, action: PayloadAction<DyadWithPasscode>) => {
            dyadEntityAdapter.addOne(state.dyadsEntityState, action.payload)
        },
        _setFreeTopicDetails: (state, action: PayloadAction<{dyad_id: string, details: Array<FreeTopicDetail>}>) => {
            state.mountedDyadId = action.payload.dyad_id
            freeTopicDetailEntityAdapter.setAll(state.freeTopicDetailsEntityState, action.payload.details)
        },
        _removeFreeTopicById: (state, action: PayloadAction<string>) => {
            freeTopicDetailEntityAdapter.removeOne(state.freeTopicDetailsEntityState, action.payload)
        }
    }
})

export const dyadsSelectors = dyadEntityAdapter.getSelectors((state: AdminCoreState) => state.dyads.dyadsEntityState)

export const adminFreeTopicDetailsSelectors = freeTopicDetailEntityAdapter.getSelectors((state: AdminCoreState) => state.dyads.freeTopicDetailsEntityState)

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

export function loadOneDyad(id: string): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if(state.auth.jwt != null){
            dispatch(dyadsSlice.actions._setLoadingDyadsFlag(true))
            try{
                const resp = await Http.axios.get(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID, {dyad_id: id}), {
                    headers: await Http.getSignedInHeaders(state.auth.jwt!)
                })

                dispatch(dyadsSlice.actions._setOneDyad(resp.data))

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

export function fetchFreeTopicDetailsOfDyad(dyadId: string): AdminCoreThunk {
    return async (dispatch, getState) => {
      const state = getState()
      if(state.auth.jwt != null && state.dyads.isLoadingFreeTopics === false) {
        dispatch(dyadsSlice.actions._setLoadingFreeTopicsFlag(true))
        try{
          const resp = await Http.axios.get(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_FREE_TOPICS, {dyad_id: dyadId}), {
            headers: await Http.getSignedInHeaders(state.auth.jwt)
          })
          if(resp.status == 200){
            if(resp.data.dyad_id === dyadId){
                console.log(resp.data)
                dispatch(dyadsSlice.actions._setFreeTopicDetails(resp.data)) 
            }
          }
        }catch(ex){
          console.log(ex)
        }finally{
          dispatch(dyadsSlice.actions._setLoadingFreeTopicsFlag(false))
        }
      }
    }
  }

  export function removeFreeTopicDetailById(dyadId: string, detailId: string): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if(state.auth.jwt != null) {
            dispatch(dyadsSlice.actions._setUpdatingFreeTopicsFlag(true))
            try{
                const resp = await Http.axios.delete(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_FREE_TOPICS_ID, {dyad_id: dyadId, detail_id: detailId}), {
                    headers: await Http.getSignedInHeaders(state.auth.jwt)
                })
            if(resp.status == 200){
                dispatch(dyadsSlice.actions._removeFreeTopicById(detailId))
            }
            }catch(ex){
                console.log(ex)
            }finally{
                dispatch(dyadsSlice.actions._setUpdatingFreeTopicsFlag(false))
            }
        }
    }
  }

export default dyadsSlice.reducer
