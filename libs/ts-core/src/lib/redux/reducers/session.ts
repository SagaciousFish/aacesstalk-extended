import {
  CardCategory,
  CardInfo,
  ChildCardRecommendationResult,
  DialogueRole,
  ParentExampleMessage,
  ParentGuideElement,
  ParentGuideRecommendationResult,
  SessionTopicInfo
} from '../../model-types';
import { Action, createEntityAdapter, createSelector, createSlice, EntityAdapter, EntitySelectors, EntityState, PayloadAction, ThunkDispatch } from '@reduxjs/toolkit';
import { CoreState, CoreThunk } from '../store';
import { Http } from '../../net/http';
import { finishAfterMinimumDelay } from '@aacesstalk/libs/ts-core';
const group = require('group-array')

const parentGuideAdapter = createEntityAdapter<ParentGuideElement>()
const INITIAL_PARENT_GUIDE_STATE = parentGuideAdapter.getInitialState()

const selectedCardAdapter = createEntityAdapter<CardInfo>()
const INITIAL_SELECTED_CARD_STATE = selectedCardAdapter.getInitialState()

const CARD_CATEGORIES = [CardCategory.Action, CardCategory.Emotion, CardCategory.Topic, CardCategory.Core]

type ChildCardTypeAdapters = {[key in CardCategory | string]: {
  adapter: EntityAdapter<CardInfo, string>,
  initialState: EntityState<CardInfo, string> 
}}

const childCardAdapters: ChildCardTypeAdapters = Object.fromEntries(CARD_CATEGORIES.map(category => {
  const adapter = createEntityAdapter<CardInfo>()
  return [category, {
    adapter, initialState: adapter.getInitialState() 
  }]
})) as ChildCardTypeAdapters

function forEachChildCardAdapters(handler:(category: CardCategory, adapter: EntityAdapter<CardInfo, string>) => void){
  Object.keys(childCardAdapters).forEach(category => {
    handler(category as CardCategory, childCardAdapters[category].adapter)
  })
}

export interface SessionState {
  id: string | undefined
  topic?: SessionTopicInfo | undefined
  currentTurn: DialogueRole
  interimCards?: Array<CardInfo>
  parentGuideRecommendationId?: string
  parentGuideEntityState: typeof INITIAL_PARENT_GUIDE_STATE

  numTurns: number

  parentExampleMessages: { [key: string]: ParentExampleMessage }

  parentExampleMessageLoadingFlags: { [key: string]: boolean }

  childCardEntityStateByCategory: {[key in CardCategory]: EntityState<CardInfo, string> },
  childCardRecommendationId?: string

  selectedChildCardEntityState: typeof INITIAL_SELECTED_CARD_STATE

  isInitializing: boolean,
  isClosingSession: boolean,
  isProcessingRecommendation: boolean,
  isGeneratingParentExample: boolean,
  error?: string
}

export const INITIAL_SESSION_STATE: SessionState = {
  id: undefined,
  topic: undefined,
  currentTurn: DialogueRole.Parent,

  parentGuideEntityState: INITIAL_PARENT_GUIDE_STATE,
  parentGuideRecommendationId: undefined,
  parentExampleMessages: {},
  parentExampleMessageLoadingFlags: {},

  childCardEntityStateByCategory: Object.fromEntries(Object.keys(childCardAdapters).map(key => [key, (childCardAdapters as any)[key].initialState])) as any,
  childCardRecommendationId: undefined,

  selectedChildCardEntityState: INITIAL_SELECTED_CARD_STATE,

  isInitializing: false,
  isClosingSession: false,
  isProcessingRecommendation: false,
  isGeneratingParentExample: false,
  error: undefined,
  numTurns: 0
}

const sessionSlice = createSlice({
  name: "session",
  initialState: INITIAL_SESSION_STATE,
  reducers: {
    initialize: () => { return { ...INITIAL_SESSION_STATE } },
    setSessionInitInfo: (state, action: PayloadAction<{ topic: SessionTopicInfo }>) => {
      state.topic = action.payload.topic
      state.currentTurn = DialogueRole.Parent 
    },
    _mountNewSession: (state, action: PayloadAction<{ id: string, topic: SessionTopicInfo }>) => {

      for (const key in INITIAL_SESSION_STATE) {
        (state as any)[key] = (INITIAL_SESSION_STATE as any)[key]
      }

      state.id = action.payload.id
      state.topic = action.payload.topic
      state.currentTurn = DialogueRole.Parent      
    },

    _setInitializingFlag: (state, action: PayloadAction<boolean>) => {
      state.isInitializing = action.payload
    },

    _setClosingFlag: (state, action: PayloadAction<boolean>) => {
      state.isClosingSession = action.payload
    },

    _setLoadingFlag: (state, action: PayloadAction<{ key: keyof SessionState, flag: boolean }>) => {
      (state as any)[action.payload.key] = action.payload.flag
    },

    _setError: (state, action: PayloadAction<string | undefined>) => {
      state.error = action.payload
    },

    _setNextTurn: (state, action: PayloadAction<DialogueRole>) => {
      state.currentTurn = action.payload
    },

    _incNumTurn: (state) => {
      state.numTurns++
    },

    _storeNewParentGuideRecommendation: (state, action: PayloadAction<ParentGuideRecommendationResult>) => {
      parentGuideAdapter.removeAll(state.parentGuideEntityState)
      parentGuideAdapter.addMany(state.parentGuideEntityState, action.payload.guides)
      state.parentGuideRecommendationId = action.payload.id
      state.parentExampleMessageLoadingFlags = {}
      state.parentExampleMessages = {}
    },

    _setGuideExampleMessageLoadingFlag: (state, action: PayloadAction<{ guideId: string, flag: boolean }>) => {
      state.parentExampleMessageLoadingFlags[action.payload.guideId] = action.payload.flag
    },

    _addGuideExampleMessage: (state, action: PayloadAction<ParentExampleMessage>) => {
      if (action.payload.guide_id) {
        state.parentExampleMessageLoadingFlags[action.payload.guide_id] = false
        state.parentExampleMessages[action.payload.guide_id] = action.payload
      }
    },

    _storeNewChildCardRecommendation: (state, action: PayloadAction<ChildCardRecommendationResult>) => {
      
      const cardGroupByCategory = group(action.payload.cards, "category")

      forEachChildCardAdapters((category, adapter) => {

        const previousCardEntityState = state.childCardEntityStateByCategory[category]
        const newCardInfos: Array<CardInfo> = cardGroupByCategory[category]

        const reorderedNewCardInfos: Array<CardInfo> = new Array(newCardInfos.length).fill(null)

        // Index matching
        const indexMap = new Map<string, number>()
        const unmatchedElements: Array<CardInfo> = []

        previousCardEntityState.ids.forEach((id, index) => {
          indexMap.set(previousCardEntityState.entities[id].label_localized, index)
        })

        newCardInfos.forEach((cardInfo) => {
          if(indexMap.has(cardInfo.label_localized)){
            reorderedNewCardInfos[indexMap.get(cardInfo.label_localized)!!] = cardInfo
          }else{
            unmatchedElements.push(cardInfo)
          }
        })

        let fillIndex=  0;
        unmatchedElements.forEach(cardInfo => {
          while(reorderedNewCardInfos[fillIndex] !== null && fillIndex < reorderedNewCardInfos.length){
            fillIndex++;
          }
          if(fillIndex < reorderedNewCardInfos.length){
            reorderedNewCardInfos[fillIndex] = cardInfo
          }
        })


        adapter.removeAll(state.childCardEntityStateByCategory[category])
        adapter.addMany(state.childCardEntityStateByCategory[category], reorderedNewCardInfos)
      })

      state.childCardRecommendationId = action.payload.id
    },

    _appendSelectedCard: (state, action: PayloadAction<CardInfo>) => {
      selectedCardAdapter.addOne(state.selectedChildCardEntityState, action.payload) 
    },

    _popLastSelectedCard: (state) => {
      const numSelectedCards = state.selectedChildCardEntityState.ids.length
      if(numSelectedCards > 0){
        selectedCardAdapter.removeOne(state.selectedChildCardEntityState, state.selectedChildCardEntityState.ids[numSelectedCards - 1]) 
      }
    },

    _claerCardRecommendation: (state) => {
      selectedCardAdapter.removeAll(state.selectedChildCardEntityState)
      forEachChildCardAdapters((category, adapter) => {
        adapter.removeAll(state.childCardEntityStateByCategory[category])
      })
      state.childCardRecommendationId = undefined
    }
  },

})

export const selectedChildCardSelectors = selectedCardAdapter.getSelectors<CoreState>(state => state.session.selectedChildCardEntityState)

export const childCardSessionSelectors = Object.fromEntries(CARD_CATEGORIES.map(category => [category, childCardAdapters[category].adapter.getSelectors<CoreState>(state => state.session.childCardEntityStateByCategory[category])]))

export const parentGuideSelectors = parentGuideAdapter.getSelectors<CoreState>(state => state.session.parentGuideEntityState)

export const parentGuideMessageSelector = createSelector(
  [parentGuideSelectors.selectById],
  (guide) => {
    return guide.guide_localized || guide.guide
  }
)

export const isChildCardConfirmValidSelector = createSelector(
  [selectedChildCardSelectors.selectIds],
  (ids) => {
    return ids.length > 0
  } 
)

function makeSignedInThunk(
  options: {
    loadingFlagKey?: keyof SessionState,
    runIfSignedIn?: (dispatch: ThunkDispatch<CoreState, unknown, Action<string>>, getState: () => CoreState, signedInHeader: any) => Promise<void>,
    runIfNotSignedIn?: (dispatch: ThunkDispatch<CoreState, unknown, Action<string>>, getState: () => CoreState) => Promise<void>,
    onError?: (ex: any, dispatch: ThunkDispatch<CoreState, unknown, Action<string>>, getState: () => CoreState) => Promise<void>,
    onFinally?: (dispatch: ThunkDispatch<CoreState, unknown, Action<string>>, getState: () => CoreState, error?: any) => Promise<void>
  },
  checkSessionId: boolean = false
): CoreThunk {
  return async (dispatch, getState) => {
    const state = getState()
    if (state.auth.jwt && options.runIfSignedIn && (checkSessionId == false || state.session.id != null)) {
      if (options.loadingFlagKey) {
        dispatch(sessionSlice.actions._setLoadingFlag({ key: options.loadingFlagKey, flag: true }))
      }
      let error = null
      try {
        const header = await Http.getSignedInHeaders(state.auth.jwt)
        await options.runIfSignedIn(dispatch, getState, header)
        
      } catch (ex: any) {
        if (options.onError) {
          await options.onError(ex, dispatch, getState)
        }
        error = ex
      } finally {
        if (options.onFinally) {
          await options.onFinally(dispatch, getState, error)
        }
        if (options.loadingFlagKey) {
          dispatch(sessionSlice.actions._setLoadingFlag({ key: options.loadingFlagKey, flag: false }))
        }
      }
    } else if (options.runIfNotSignedIn) {
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
        dispatch(sessionSlice.actions.setSessionInitInfo({ topic }))
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


export function endSession(onComplete?: (success: boolean) => Promise<void>): CoreThunk {
  return makeSignedInThunk(
    {
      runIfSignedIn: async (dispatch, getState, header) => {
        dispatch(sessionSlice.actions._setClosingFlag(true))
        const state = getState()
        await Http.axios.put(Http.getTemplateEndpoint(Http.ENDPOINT_DYAD_SESSION_END, { session_id: state.session.id!! }), null, {
          headers: header
        })
      },
      onError: async (ex, dispatch) => {
        console.log("Session ending error")
        console.error(ex)
        dispatch(sessionSlice.actions._setError("Session ending error."))
      },
      onFinally: async (dispatch, _, error) => {
        dispatch(sessionSlice.actions._setClosingFlag(false))
        dispatch(sessionSlice.actions.initialize())
        if(onComplete){
          await onComplete(error == null)
        }
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
        const resp = await Http.axios.delete(Http.getTemplateEndpoint(Http.ENDPOINT_DYAD_SESSION_ABORT, { session_id: state.session.id!! }), {
          headers: header
        })
      },
      onFinally: async (dispatch, _, error) => {
        dispatch(sessionSlice.actions.initialize())
      }
    },
    true
  )
}

/////////////////////////////////////////////////////////////////


// Parent messaging /////////////////////////////////////////////

export function startAndRetrieveInitialParentGuide(): CoreThunk {
  return makeSignedInThunk(
    {
      loadingFlagKey: 'isProcessingRecommendation',
      runIfSignedIn: async (dispatch, getState, header) => {
        console.log("Request parent guides...")
        const state = getState()
        const resp = await finishAfterMinimumDelay(Http.axios.post(Http.getTemplateEndpoint(Http.ENDPOINT_DYAD_SESSION_START, { session_id: state.session.id!! }), null, {
          headers: header
        }), 0)
        console.log("Retrieved parent guides.")
        const result: ParentGuideRecommendationResult = resp.data
        dispatch(sessionSlice.actions._storeNewParentGuideRecommendation(result))
      }
    }, true
  )
}

export function requestParentGuideExampleMessage(guideId: string, onComplete?: (message: ParentExampleMessage) => void): CoreThunk {
  return makeSignedInThunk({
    runIfSignedIn: async (dispatch, getState, header) => {
      dispatch(sessionSlice.actions._setGuideExampleMessageLoadingFlag({ guideId, flag: true }))
      const state = getState()
      const resp = await finishAfterMinimumDelay(Http.axios.post(Http.getTemplateEndpoint(Http.ENDPOINT_DYAD_MESSAGE_PARENT_EXAMPLE, { session_id: state.session.id!! }), {
        guide_id: guideId,
        recommendation_id: state.session.parentGuideRecommendationId
      }, {
        headers: header
      }), 0)
      const exampleMessage: ParentExampleMessage = resp.data
      dispatch(sessionSlice.actions._addGuideExampleMessage(exampleMessage))
      onComplete?.(exampleMessage)
    },

    onFinally: async (dispatch) => {
      dispatch(sessionSlice.actions._setGuideExampleMessageLoadingFlag({ guideId, flag: false }))
    }
  }, true)
}

export function submitParentMessage(message: string): CoreThunk {
  return makeSignedInThunk({
    loadingFlagKey: 'isProcessingRecommendation',
    runIfSignedIn: async (dispatch, getState, signedInHeader) => {
      const state = getState()

      console.log("Send parent message and retrieve child card recommendation...")

      dispatch(sessionSlice.actions._incNumTurn())
      dispatch(sessionSlice.actions._setNextTurn(DialogueRole.Child))

      const resp = await Http.axios.post(Http.getTemplateEndpoint(Http.ENDPOINT_DYAD_MESSAGE_PARENT_SEND_MESSAGE, { session_id: state.session.id!! }), {
        message,
        //recommendation_id: state.session.parentGuideRecommendationId
      }, {
        headers: signedInHeader
      })

      console.log("Retrieved new child card recommendations.")

      const cardRecommendationResult: ChildCardRecommendationResult = resp.data
      dispatch(sessionSlice.actions._storeNewChildCardRecommendation(cardRecommendationResult))
    },
    onError: async (ex) => {
      console.log(ex)
    }
  }, true)
}

export function appendCard(cardInfo: CardInfo): CoreThunk {
  return makeSignedInThunk({
    loadingFlagKey: 'isProcessingRecommendation',
    runIfSignedIn: async (dispatch, getState, headers) => {
      const state = getState()

      dispatch(sessionSlice.actions._appendSelectedCard(cardInfo))

      const resp = await Http.axios.post(Http.getTemplateEndpoint(Http.ENDPOINT_DYAD_MESSAGE_CHILD_APPEND_CARD, { session_id: state.session.id!! }), 
        { id: cardInfo.id, recommendation_id: cardInfo.recommendation_id }, 
        { headers })

      const { new_recommendation } = resp.data

      dispatch(sessionSlice.actions._storeNewChildCardRecommendation(new_recommendation))

    },
    onError: async (ex) => {
      console.log(ex)
    }
    
  }, true)
}

export function removeLastCard(): CoreThunk {
  return makeSignedInThunk({
    loadingFlagKey: "isProcessingRecommendation",
    runIfSignedIn: async (dispatch, getState, headers) => {
      const state = getState()

      dispatch(sessionSlice.actions._popLastSelectedCard())

      const resp = await Http.axios.put(Http.getTemplateEndpoint(Http.ENDPOINT_DYAD_MESSAGE_CHILD_POP_LAST_CARD, { session_id: state.session.id!! }), null, {
        headers
      })

      const { new_recommendation } = resp.data

      dispatch(sessionSlice.actions._storeNewChildCardRecommendation(new_recommendation))

    }
  }, true)
}

export function refreshCards(): CoreThunk {
  return makeSignedInThunk({
    loadingFlagKey: "isProcessingRecommendation",
    runIfSignedIn: async (dispatch, getState, headers) => {
      const state = getState()

      const resp = await Http.axios.put(Http.getTemplateEndpoint(Http.ENDPOINT_DYAD_MESSAGE_CHILD_REFRESH_CARDS, { session_id: state.session.id!! }), null, {
        headers
      })

      const new_recommendation = resp.data

      dispatch(sessionSlice.actions._storeNewChildCardRecommendation(new_recommendation))

    }
  }, true)
}


export function confirmSelectedCards(): CoreThunk {
  return makeSignedInThunk({
    loadingFlagKey: "isProcessingRecommendation",
    runIfSignedIn: async (dispatch, getState, headers) => {
      const state = getState()
      dispatch(sessionSlice.actions._claerCardRecommendation())
      dispatch(sessionSlice.actions._incNumTurn())
      dispatch(sessionSlice.actions._setNextTurn(DialogueRole.Parent))

      const resp = await Http.axios.post(Http.getTemplateEndpoint(Http.ENDPOINT_DYAD_MESSAGE_CHILD_CONFIRM_CARDS, { session_id: state.session.id!! }), null, {
        headers
      })

      const new_recommendation = resp.data

      dispatch(sessionSlice.actions._storeNewParentGuideRecommendation(new_recommendation))

    }
  }, true)
}

export const { setSessionInitInfo } = sessionSlice.actions

export default sessionSlice.reducer

