import {
  CardInfo,
  ChildCardRecommendationResult,
  DialogueRole,
  ParentExampleMessage,
  ParentGuideRecommendationResult
} from '../../model-types';
import { createSlice, Dispatch, PayloadAction } from '@reduxjs/toolkit';
import { CoreThunk } from '../store';
import { Http } from '../../net/http';

export interface SessionState{
  id: string | undefined
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
  parentExampleMessages: {},
  isProcessing: false,
  error: undefined
}

const sessionSlice = createSlice({
  name: "session",
  initialState: INITIAL_SESSION_STATE,
  reducers: {
    initialize: () => {return {...INITIAL_SESSION_STATE}},
    _mountNewSession: (state, action: PayloadAction<string>) => {
      state.id = action.payload
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

export function startNewSession(): CoreThunk {
  return async (dispatch, getState) => {
    const state = getState()
    if(state.auth.jwt){
      dispatch(sessionSlice.actions._setProcessingFlag(true))
      try {
        const resp = await Http.axios.post(Http.ENDPOINT_DYAD_SESSION_NEW, null, {
          headers: await Http.getSignedInHeaders(state.auth.jwt)
        })
        const sessionId = resp.data
        dispatch(sessionSlice.actions._mountNewSession(sessionId))
      }catch(ex){
        dispatch(sessionSlice.actions._setError("Session initialization error."))
      }finally {
        dispatch(sessionSlice.actions._setProcessingFlag(false))
      }
    }
  }
}

export default sessionSlice.reducer

