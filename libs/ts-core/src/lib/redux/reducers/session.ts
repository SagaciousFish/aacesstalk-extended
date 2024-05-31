import {
  CardInfo,
  ChildCardRecommendationResult,
  DialogueRole,
  ParentExampleMessage,
  ParentGuideRecommendationResult,
  SessionTopicInfo
} from '../../model-types';
import { Action, createSlice, PayloadAction, ThunkDispatch } from '@reduxjs/toolkit';
import { CoreState, CoreThunk } from '../store';
import { Http } from '../../net/http';

export interface SessionState{
  id: string | undefined
  topic?: SessionTopicInfo
  currentTurn?: DialogueRole
  interimCards?: Array<CardInfo>
  parentGuideRecommendation?: ParentGuideRecommendationResult
  childCardRecommendation?: ChildCardRecommendationResult

  parentExampleMessages: {[key:string]: ParentExampleMessage}

  isProcessing: boolean,
  error? : string
}

export const INITIAL_SESSION_STATE: SessionState = {
  id: undefined,
  topic: undefined,
  parentExampleMessages: {},
  isProcessing: false,
  error: undefined
}

const sessionSlice = createSlice({
  name: "session",
  initialState: INITIAL_SESSION_STATE,
  reducers: {
    initialize: () => {return {...INITIAL_SESSION_STATE}},
    _mountNewSession: (state, action: PayloadAction<{id: string, topic: SessionTopicInfo}>) => {
      state.id = action.payload.id
      state.topic = action.payload.topic
      state.currentTurn = DialogueRole.Parent
      state.interimCards = undefined
      state.parentExampleMessages = {}
      state.childCardRecommendation= undefined
      state.parentGuideRecommendation = undefined
    },

    _setProcessingFlag: (state, action: PayloadAction<boolean>) => {
      state.isProcessing = action.payload
    },

    _setError: (state, action: PayloadAction<string|undefined>) => {
      state.error = action.payload
    }
  }
})

function makeSignedInThunk(
  handlers: {
    runIfSignedIn?: (dispatch: ThunkDispatch<CoreState, unknown, Action<string>>, getState: ()=>CoreState, signedInHeader: any) => Promise<void>,
    runIfNotSignedIn?: (dispatch: ThunkDispatch<CoreState, unknown, Action<string>>, getState: ()=>CoreState) => Promise<void>,
    onError?: (ex: any, dispatch: ThunkDispatch<CoreState, unknown, Action<string>>, getState: ()=>CoreState) => Promise<void>,
    onFinally?: (dispatch: ThunkDispatch<CoreState, unknown, Action<string>>, getState: ()=>CoreState) => Promise<void>
  },
  checkSessionId: boolean = false
): CoreThunk {
  return async (dispatch, getState) => {
    const state = getState()
    if(state.auth.jwt && handlers.runIfSignedIn && (checkSessionId == false || state.session.id != null)){
      dispatch(sessionSlice.actions._setProcessingFlag(true))
      try {
        const header = await Http.getSignedInHeaders(state.auth.jwt)
        await handlers.runIfSignedIn(dispatch, getState, header)
      }catch(ex: any){
        if(handlers.onError){
          await handlers.onError(ex, dispatch, getState)
        }
      }finally {
        if(handlers.onFinally){
          await handlers.onFinally(dispatch, getState)
        }
        dispatch(sessionSlice.actions._setProcessingFlag(false))
      }
    }else if(handlers.runIfNotSignedIn){
      await handlers.runIfNotSignedIn(dispatch, getState)
    }
  }
}

export function startNewSession(topic: SessionTopicInfo, timezone: string): CoreThunk {
  return makeSignedInThunk(
    {
      runIfSignedIn: async (dispatch, getState, header) => {
        console.log("Init session...")
        const resp = await Http.axios.post(Http.ENDPOINT_DYAD_SESSION_NEW, { topic, timezone }, {
          headers: header
        })
        const sessionId = resp.data
        dispatch(sessionSlice.actions._mountNewSession({ id: sessionId, topic }))
      },
      onError: async (ex, dispatch, getState) => {
        console.error(ex)
        dispatch(sessionSlice.actions._setError("Session initialization error."))
      }
    })
}


export function endSession(): CoreThunk {
  return makeSignedInThunk(
    {
      runIfSignedIn: async (dispatch, getState, header) => {
        const state = getState()
        await Http.axios.put(Http.getTemplateEndpoint(Http.ENDPOINT_DYAD_SESSION_END, {session_id: state.session.id!!}), {
          headers: header
        })
        dispatch(sessionSlice.actions.initialize())
      },
      onError: async (ex, dispatch) => {
        console.log("Session ending error")
        dispatch(sessionSlice.actions._setError("Session ending error."))
      }
    },
    true
  )
}

export function cancelSession(): CoreThunk {
  return makeSignedInThunk(
    {
      runIfSignedIn: async (dispatch, getState, header) => {
        const state = getState()
        const resp = await Http.axios.delete(Http.getTemplateEndpoint(Http.ENDPOINT_DYAD_SESSION_ABORT, {session_id: state.session.id!!}), {
          headers: header
        })
      },
      onFinally: async (dispatch) => {
        dispatch(sessionSlice.actions.initialize())
      }
    }, 
    true
  )
}

export default sessionSlice.reducer

