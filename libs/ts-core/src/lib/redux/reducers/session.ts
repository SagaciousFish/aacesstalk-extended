import {
  CardInfo,
  ChildCardRecommendationResult,
  DialogueRole,
  ParentExampleMessage,
  ParentGuideElement,
  ParentGuideRecommendationResult,
  SessionTopicInfo
} from '../../model-types';
import { Action, createEntityAdapter, createSlice, PayloadAction, ThunkDispatch } from '@reduxjs/toolkit';
import { CoreState, CoreThunk } from '../store';
import { Http } from '../../net/http';

const parentGuideAdapter = createEntityAdapter<ParentGuideElement>()
const INITIAL_PARENT_GUIDE_STATE = parentGuideAdapter.getInitialState()

export interface SessionState{
  id: string | undefined
  topic?: SessionTopicInfo
  currentTurn?: DialogueRole
  interimCards?: Array<CardInfo>
  parentGuideRecommendationId?: string
  parentGuideEntityState: typeof INITIAL_PARENT_GUIDE_STATE
  childCardRecommendation?: ChildCardRecommendationResult

  parentExampleMessages: {[key:string]: ParentExampleMessage}

  isInitializing: boolean,
  isProcessingRecommendation: boolean,
  isGeneratingParentExample: boolean,
  error? : string
}

export const INITIAL_SESSION_STATE: SessionState = {
  id: undefined,
  topic: undefined,
  parentGuideEntityState: INITIAL_PARENT_GUIDE_STATE,
  parentGuideRecommendationId: undefined,
  isInitializing: false,
  isProcessingRecommendation: false,
  isGeneratingParentExample: false,
  error: undefined,
  parentExampleMessages: {}
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
      state.parentGuideRecommendationId = undefined
      state.isGeneratingParentExample = false
      state.isProcessingRecommendation =false
      parentGuideAdapter.removeAll(state.parentGuideEntityState)
    },

    _setInitializingFlag: (state, action: PayloadAction<boolean>) => {
      state.isInitializing = action.payload
    },

    _setLoadingFlag: (state, action: PayloadAction<{key: keyof SessionState, flag: boolean}>) => {
      (state as any)[action.payload.key] = action.payload.flag
    },

    _setError: (state, action: PayloadAction<string|undefined>) => {
      state.error = action.payload
    },

    _setNextTurn: (state, action: PayloadAction<DialogueRole>) => {
      state.currentTurn = action.payload
    },

    _storeNewParentGuideRecommendation: (state, action: PayloadAction<ParentGuideRecommendationResult>) => {
      parentGuideAdapter.removeAll(state.parentGuideEntityState)
      parentGuideAdapter.addMany(state.parentGuideEntityState, action.payload.guides)
      state.parentGuideRecommendationId = action.payload.id
    }
  }
})

function makeSignedInThunk(
  options: {
    loadingFlagKey?: keyof SessionState,
    runIfSignedIn?: (dispatch: ThunkDispatch<CoreState, unknown, Action<string>>, getState: ()=>CoreState, signedInHeader: any) => Promise<void>,
    runIfNotSignedIn?: (dispatch: ThunkDispatch<CoreState, unknown, Action<string>>, getState: ()=>CoreState) => Promise<void>,
    onError?: (ex: any, dispatch: ThunkDispatch<CoreState, unknown, Action<string>>, getState: ()=>CoreState) => Promise<void>,
    onFinally?: (dispatch: ThunkDispatch<CoreState, unknown, Action<string>>, getState: ()=>CoreState) => Promise<void>
  },
  checkSessionId: boolean = false
): CoreThunk {
  return async (dispatch, getState) => {
    const state = getState()
    if(state.auth.jwt && options.runIfSignedIn && (checkSessionId == false || state.session.id != null)){
      if(options.loadingFlagKey){
        dispatch(sessionSlice.actions._setLoadingFlag({key: options.loadingFlagKey, flag: true}))
      }
      try {
        const header = await Http.getSignedInHeaders(state.auth.jwt)
        await options.runIfSignedIn(dispatch, getState, header)
      }catch(ex: any){
        if(options.onError){
          await options.onError(ex, dispatch, getState)
        }
      }finally {
        if(options.onFinally){
          await options.onFinally(dispatch, getState)
        }
        if(options.loadingFlagKey){
          dispatch(sessionSlice.actions._setLoadingFlag({key: options.loadingFlagKey, flag: false}))
        }
      }
    }else if(options.runIfNotSignedIn){
      await options.runIfNotSignedIn(dispatch, getState)
    }
  }
}

// Session methods //////////////////////////

export function startNewSession(topic: SessionTopicInfo, timezone: string): CoreThunk {
  return makeSignedInThunk(
    {
      runIfSignedIn: async (dispatch, getState, header) => {
        console.log("Init session...")
        dispatch(sessionSlice.actions._setInitializingFlag(true))
        const resp = await Http.axios.post(Http.ENDPOINT_DYAD_SESSION_NEW, { topic, timezone }, {
          headers: header
        })
        const sessionId = resp.data
        dispatch(sessionSlice.actions._mountNewSession({ id: sessionId, topic }))
      },
      onError: async (ex, dispatch, getState) => {
        console.error(ex)
        dispatch(sessionSlice.actions._setError("Session initialization error."))
      },
      onFinally: async (dispatch, getState) => {
        dispatch(sessionSlice.actions._setInitializingFlag(false))
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

/////////////////////////////////////////////////////////////////


// Parent messaging /////////////////////////////////////////////

export function requestParentGuides(): CoreThunk {
  return makeSignedInThunk(
    {
      loadingFlagKey: 'isProcessingRecommendation',
      runIfSignedIn: async (dispatch, getState, header) => {
        console.log("Request parent guides...")
        const state = getState()
        const resp = await Http.axios.post(Http.getTemplateEndpoint(Http.ENDPOINT_DYAD_MESSAGE_PARENT_GUIDE, { session_id: state.session.id!! }), null, {
          headers: header
        })
        console.log("Retrieved parent guides.")
        const result: ParentGuideRecommendationResult = resp.data
        dispatch(sessionSlice.actions._storeNewParentGuideRecommendation(result))
      }
    }, true
  )
}


export default sessionSlice.reducer

