import { Dyad, FreeTopicDetail, ParentType } from '../../model-types';
import { createEntityAdapter, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { CoreState, CoreThunk } from '../store';
import { Http } from '../../net/http';
import { jwtDecode } from "jwt-decode";
import { Axios, AxiosError } from 'axios';
import { AACessTalkErrors } from '../../errors';
import { initializeDyadStatus } from './dyad-status';

const freeTopicDetailEntityAdapter = createEntityAdapter<FreeTopicDetail>()
const INITIAL_FREE_TOPIC_DETAIL_STATE = freeTopicDetailEntityAdapter.getInitialState()

export interface AuthState {
  isAuthorizing: boolean;
  jwt?: string;
  dyadInfo?: Dyad;
  isLoadingFreeTopicDetails: boolean
  freeTopicDetailEntityState: typeof INITIAL_FREE_TOPIC_DETAIL_STATE,
  error?: string;
}

const INITIAL_AUTH_STATE: AuthState = {
  isAuthorizing: false,
  isLoadingFreeTopicDetails: false,
  freeTopicDetailEntityState: INITIAL_FREE_TOPIC_DETAIL_STATE
};

const authSlice = createSlice({
  name: 'auth',
  initialState: INITIAL_AUTH_STATE,
  reducers: {
    initialize: () => {
      return { ...INITIAL_AUTH_STATE };
    },

    _authorizingFlagOn: (state) => {
      state.isAuthorizing = true;
      state.dyadInfo = undefined;
      state.jwt = undefined;
    },

    _authorizingFlagOff: (state) => {
      state.isAuthorizing = false;
    },

    _setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
    },

    _setSignedInUser: (state, action: PayloadAction<{ dyad: Dyad, token: string }>) => {
      state.isAuthorizing = false;
      state.dyadInfo = action.payload.dyad;
      state.jwt = action.payload.token;
      state.error = undefined;
    },

    _setFreeTopicDetailLoadingFlag: (state, action: PayloadAction<boolean>) => {
      state.isLoadingFreeTopicDetails = action.payload
    },

    _setFreeTopicDetails: (state, action: PayloadAction<Array<FreeTopicDetail>>) => {
      freeTopicDetailEntityAdapter.setAll(state.freeTopicDetailEntityState, action.payload)
    }
  }
});

export const freeTopicDetailSelectors = freeTopicDetailEntityAdapter.getSelectors((state: CoreState) => state.auth.freeTopicDetailEntityState)

export function loginDyadThunk(code: string): CoreThunk {
  return async (dispatch, getState) => {
    dispatch(authSlice.actions._authorizingFlagOn());

    try {
      const tokenResponse = await Http.axios.post(Http.ENDPOINT_DYAD_ACCOUNT_LOGIN,
        { code }, {
          headers: {
            'Content-Type': 'application/json'
          }
        });

      const { jwt, free_topics } = tokenResponse.data

      const decoded = jwtDecode<{
        sub: string,
        alias: string,
        child_name: string,
        parent_type: ParentType,
        iat: number,
        exp: number}>(jwt)

      console.log(free_topics)

      dispatch(authSlice.actions._setSignedInUser({
        dyad: {
          id: decoded.sub,
          child_name: decoded.child_name,
          parent_type: decoded.parent_type,
          alias: decoded.alias
        },
        token: jwt
      }));

      if(free_topics != null){
        dispatch(authSlice.actions._setFreeTopicDetails(free_topics))
      }else{
        dispatch(authSlice.actions._setFreeTopicDetails([]))
      }

    } catch (ex) {
      let error = AACessTalkErrors.UnknownError 
      if(ex instanceof AxiosError){
        if(ex.code == AxiosError.ERR_NETWORK){
          error = AACessTalkErrors.ServerNotResponding
        }else if (ex.response?.status == 400){
          error = AACessTalkErrors.WrongCredential
        }
      }
      dispatch(authSlice.actions._setError(error))
    } finally {
      dispatch(authSlice.actions._setFreeTopicDetailLoadingFlag(false))
      dispatch(authSlice.actions._authorizingFlagOff())
    }
  };
}

export function signOutDyadThunk(): CoreThunk {
  return async (dispatch, getState) => {
    dispatch(authSlice.actions.initialize())
    dispatch(initializeDyadStatus())
  }
}

export function fetchFreeTopicDetails(): CoreThunk {
  return async (dispatch, getState) => {
    const state = getState()
    if(state.auth.jwt != null && state.auth.isLoadingFreeTopicDetails === false) {
      dispatch(authSlice.actions._setFreeTopicDetailLoadingFlag(true))
      try{
        const resp = await Http.axios.get(Http.ENDPOINT_DYAD_DATA_FREE_TOPICS, {
          headers: await Http.getSignedInHeaders(state.auth.jwt)
        })
        if(resp.status == 200){
          if(resp.data.dyad_id === state.auth.dyadInfo?.id){
            dispatch(authSlice.actions._setFreeTopicDetails(resp.data.details)) 
          }
        }
      }catch(ex){
        console.log(ex)
      }finally{
        dispatch(authSlice.actions._setFreeTopicDetailLoadingFlag(false))
      }
    }
  }
}


export default authSlice.reducer;
