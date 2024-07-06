import { PayloadAction, createEntityAdapter, createSlice } from "@reduxjs/toolkit";
import { ExtendedSessionInfo, TOPIC_CATEGORIES, TopicCategory } from "../../model-types";
import { CoreState, CoreThunk } from "../store";
import { Http } from "../../net/http";
const group = require('group-array')
const moment = require('moment-timezone')

const sessionInfoEntityAdapter = createEntityAdapter<ExtendedSessionInfo>()

const sessionInfoEntityInitialState = sessionInfoEntityAdapter.getInitialState()

export interface DyadStatusState{
    sessionInfoEntityState: typeof sessionInfoEntityInitialState
    sessionInfoFetchedAt?: number
    numSessionsByTopicCategory: {[key: string | TopicCategory] : {today: number, total: number}}
    isFetchingSessionInfo: boolean
}

const INITIAL_STATE: DyadStatusState = {
    sessionInfoEntityState: sessionInfoEntityInitialState,
    sessionInfoFetchedAt: undefined,
    numSessionsByTopicCategory: {},
    isFetchingSessionInfo: false
}

const dyadStatusSlice = createSlice({
    name: "dyad-status",
    initialState: INITIAL_STATE,
    reducers: {
        initialize: (state) => INITIAL_STATE,

        _clearSessionInfos: (state, action) => {
            sessionInfoEntityAdapter.removeAll(state.sessionInfoEntityState)
            state.sessionInfoFetchedAt = undefined
            state.numSessionsByTopicCategory = {}
            state.isFetchingSessionInfo = false
        },

        _setFetchingFlag: (state, action: PayloadAction<boolean>) => {
            state.isFetchingSessionInfo = action.payload
        },

        _updateSessionInfos: (state, action: PayloadAction<{
            sessions: Array<ExtendedSessionInfo>,
            fetchedAt: number,
            fetchedTimezone: string
        }>) => {

            console.log("Update session infos")

            sessionInfoEntityAdapter.setAll(state.sessionInfoEntityState, action.payload.sessions)

            const grouped = group(action.payload.sessions, "topic.category")
            
            const numSessionsByTopicCategory: {[key: string | TopicCategory] : {today: number, total: number}} = {}

            const refTime = moment.tz(action.payload.fetchedAt, action.payload.fetchedTimezone)

            for(const category of TOPIC_CATEGORIES){
                if(grouped[category] != null){
                    numSessionsByTopicCategory[category] = {today: grouped[category].filter((session: ExtendedSessionInfo) => {
                        const zonedSessionTime = moment.tz(session.started_timestamp, session.local_timezone)
                        return zonedSessionTime.isSame(refTime, 'day')
                    }).length, total: grouped[category].length}
                }else{
                    numSessionsByTopicCategory[category] = {today: 0, total: 0}
                }
            }

            state.numSessionsByTopicCategory = numSessionsByTopicCategory

            state.sessionInfoFetchedAt = action.payload.fetchedAt
        }
    }
})

export const sessionInfoEntitySelectors = sessionInfoEntityAdapter.getSelectors<CoreState>(state => state.dyadStatus.sessionInfoEntityState)

export function fetchSessionInfoSummaries(): CoreThunk{
    return async (dispatch, getState) => {
        const state= getState()
        if(state.auth.jwt != null && state.dyadStatus.isFetchingSessionInfo == false){
            dispatch(dyadStatusSlice.actions._setFetchingFlag(true))
            try{
                const response = await Http.axios.get(Http.ENDPOINT_DYAD_SESSION_LIST, {
                    headers: await Http.getSignedInHeaders(state.auth.jwt!)
                })

                const data: {
                    dyad_id: string,
                    sessions: Array<ExtendedSessionInfo>
                } = response.data

                if(state.auth.dyadInfo?.id === data.dyad_id){
                    dispatch(dyadStatusSlice.actions._updateSessionInfos({
                        sessions: data.sessions,
                        fetchedAt: Date.now(),
                        fetchedTimezone: await Http.getTimezone()
                    }))
                }

            }catch(ex){
                console.log("Fetching session list error - ", ex)
            }finally{
                dispatch(dyadStatusSlice.actions._setFetchingFlag(false))
            }            
        }
    }
}

export const { initialize: initializeDyadStatus } = dyadStatusSlice.actions

export default dyadStatusSlice.reducer