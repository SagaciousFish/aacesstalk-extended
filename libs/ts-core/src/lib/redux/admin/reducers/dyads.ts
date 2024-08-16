import { PayloadAction, createEntityAdapter, createSlice } from "@reduxjs/toolkit"
import { DialogueSession, DyadWithPasscode, ExtendedSessionInfo, FreeTopicDetail, UserDefinedCardInfo } from "../../../model-types"
import { AdminCoreState, AdminCoreThunk } from "../store"
import { Http } from "../../../net/http"

const dyadEntityAdapter = createEntityAdapter<DyadWithPasscode>()
const INITIAL_DYAD_ENTITY_STATE = dyadEntityAdapter.getInitialState()

const freeTopicDetailEntityAdapter = createEntityAdapter<FreeTopicDetail>()
const INITIAL_FREE_TOPIC_DETAIL_ENTITY_STATE = freeTopicDetailEntityAdapter.getInitialState()

const sessionSummaryEntityAdapter = createEntityAdapter<ExtendedSessionInfo>()
const INITIAL_SESSION_SUMMARY_ENTITY_STATE = sessionSummaryEntityAdapter.getInitialState()

const dialogueEntityAdapter = createEntityAdapter<DialogueSession>()
const INITIAL_DIALOGUE_ENTITY_STATE = dialogueEntityAdapter.getInitialState()

const userDefinedCardInfoEntityAdapter = createEntityAdapter<UserDefinedCardInfo>()
const INITIAL_USER_DEFINED_CARD_ENTITY_STATE = userDefinedCardInfoEntityAdapter.getInitialState()


export interface DyadsState {
    dyadsEntityState: typeof INITIAL_DYAD_ENTITY_STATE,
    freeTopicDetailsEntityState: typeof INITIAL_FREE_TOPIC_DETAIL_ENTITY_STATE,
    sessionSummaryEntityState: typeof INITIAL_SESSION_SUMMARY_ENTITY_STATE,
    dialogueEntityState: typeof INITIAL_DIALOGUE_ENTITY_STATE,
    userDefinedCardInfoEntityState: typeof INITIAL_USER_DEFINED_CARD_ENTITY_STATE,

    isLoadingFreeTopics: boolean,
    isLoadingDyadList: boolean,
    isUpdatingFreeTopic: boolean,
    isLoadingSessionSummaries: boolean,
    isLoadingDialogue: boolean,
    isCreatingDyad: boolean,
    isLoadingUserDefinedCards: boolean,
    mountedDyadId: string | undefined
}

const INITIAL_DYADS_STATE: DyadsState = {
    dyadsEntityState: INITIAL_DYAD_ENTITY_STATE,
    freeTopicDetailsEntityState: INITIAL_FREE_TOPIC_DETAIL_ENTITY_STATE,
    sessionSummaryEntityState: INITIAL_SESSION_SUMMARY_ENTITY_STATE,
    dialogueEntityState: INITIAL_DIALOGUE_ENTITY_STATE,
    userDefinedCardInfoEntityState: INITIAL_USER_DEFINED_CARD_ENTITY_STATE,

    isLoadingFreeTopics: false,
    isLoadingDyadList: false,
    isCreatingDyad: false,
    isLoadingSessionSummaries: false,
    isLoadingDialogue: false,
    isUpdatingFreeTopic: false,
    isLoadingUserDefinedCards: false,
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
        _setLoadingSessionSummariesFlag: (state, action: PayloadAction<boolean>) => {
            state.isLoadingSessionSummaries = action.payload
        },
        _setLoadingDialogueFlag: (state, action: PayloadAction<boolean>) => {
            state.isLoadingDialogue = action.payload
        },
        _setLoadingUserDefinedCardsFlag: (state, action: PayloadAction<boolean>) => {
            state.isLoadingUserDefinedCards = action.payload
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
        _setFreeTopicDetails: (state, action: PayloadAction<{ dyad_id: string, details: Array<FreeTopicDetail> }>) => {
            state.mountedDyadId = action.payload.dyad_id
            freeTopicDetailEntityAdapter.setAll(state.freeTopicDetailsEntityState, action.payload.details)
        },
        _setOneFreeTopicDetail: (state, action: PayloadAction<FreeTopicDetail>) => {
            freeTopicDetailEntityAdapter.setOne(state.freeTopicDetailsEntityState, action.payload)
        },
        _addOneFreeTopicDetail: (state, action: PayloadAction<FreeTopicDetail>) => {
            freeTopicDetailEntityAdapter.addOne(state.freeTopicDetailsEntityState, action.payload)
        },
        _removeFreeTopicById: (state, action: PayloadAction<string>) => {
            freeTopicDetailEntityAdapter.removeOne(state.freeTopicDetailsEntityState, action.payload)
        },

        _setSessionSummaries: (state, action: PayloadAction<Array<ExtendedSessionInfo>>) => {
            sessionSummaryEntityAdapter.setAll(state.sessionSummaryEntityState, action.payload)
        },

        _removeSessionSummary: (state, action: PayloadAction<string>) => {
            sessionSummaryEntityAdapter.removeOne(state.sessionSummaryEntityState, action.payload)
        },

        _setDialogue: (state, action: PayloadAction<DialogueSession>) => {
            dialogueEntityAdapter.setOne(state.dialogueEntityState, action.payload)
        },

        _setUserDefinedCards: (state, action: PayloadAction<Array<UserDefinedCardInfo>>) => {
            userDefinedCardInfoEntityAdapter.setAll(state.userDefinedCardInfoEntityState, action.payload)
        },

        _addOneUserDefinedCard: (state, action: PayloadAction<UserDefinedCardInfo>) => {
            userDefinedCardInfoEntityAdapter.addOne(state.userDefinedCardInfoEntityState, action.payload)
        },

        _setOneUserDefinedCard: (state, action: PayloadAction<UserDefinedCardInfo>) => {
            userDefinedCardInfoEntityAdapter.setOne(state.userDefinedCardInfoEntityState, action.payload)
        },

        _removeUserDefinedCardById: (state, action: PayloadAction<string>) => {
            userDefinedCardInfoEntityAdapter.removeOne(state.userDefinedCardInfoEntityState, action.payload)
        },

        clearDyadChildrenEntities: (state) => {
            freeTopicDetailEntityAdapter.removeAll(state.freeTopicDetailsEntityState)
            sessionSummaryEntityAdapter.removeAll(state.sessionSummaryEntityState)
            dialogueEntityAdapter.removeAll(state.dialogueEntityState)
        }
    }
})

export const dyadsSelectors = dyadEntityAdapter.getSelectors((state: AdminCoreState) => state.dyads.dyadsEntityState)

export const adminFreeTopicDetailsSelectors = freeTopicDetailEntityAdapter.getSelectors((state: AdminCoreState) => state.dyads.freeTopicDetailsEntityState)

export const adminSessionSummarySelectors = sessionSummaryEntityAdapter.getSelectors((state: AdminCoreState) => state.dyads.sessionSummaryEntityState)

export const adminDialogueSelectors = dialogueEntityAdapter.getSelectors((state: AdminCoreState) => state.dyads.dialogueEntityState)

export const userDefinedCardSelectors = userDefinedCardInfoEntityAdapter.getSelectors((state: AdminCoreState) => state.dyads.userDefinedCardInfoEntityState)

export function loadDyads(): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if (state.auth.jwt != null) {
            dispatch(dyadsSlice.actions._setLoadingDyadsFlag(true))
            try {
                const resp = await Http.axios.get(Http.ENDPOINT_ADMIN_DYADS_ALL, {
                    headers: await Http.getSignedInHeaders(state.auth.jwt!)
                })

                const { dyads } = resp.data
                dispatch(dyadsSlice.actions._setLoadedDyads(dyads))

            } catch (ex) {
                console.log(ex)
            } finally {
                dispatch(dyadsSlice.actions._setLoadingDyadsFlag(false))
            }
        }
    }
}

export function loadOneDyad(id: string): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if (state.auth.jwt != null) {
            dispatch(dyadsSlice.actions._setLoadingDyadsFlag(true))
            try {
                const resp = await Http.axios.get(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID, { dyad_id: id }), {
                    headers: await Http.getSignedInHeaders(state.auth.jwt!)
                })

                dispatch(dyadsSlice.actions._setOneDyad(resp.data))

            } catch (ex) {
                console.log(ex)
            } finally {
                dispatch(dyadsSlice.actions._setLoadingDyadsFlag(false))
            }
        }
    }
}

export function createDyad(info: any, onCreated: (dyad: DyadWithPasscode) => void, onError: (error: any) => void): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if (state.auth.jwt != null) {
            dispatch(dyadsSlice.actions._setCreatingDyadFlag(true))

            try {
                const resp = await Http.axios.post(Http.ENDPOINT_ADMIN_DYADS_NEW, info, {
                    headers: await Http.getSignedInHeaders(state.auth.jwt)
                })
                dispatch(dyadsSlice.actions._appendDyad(resp.data))
                onCreated(resp.data)
            } catch (ex) {
                console.log(ex)
                onError(ex)
            } finally {
                dispatch(dyadsSlice.actions._setCreatingDyadFlag(false))
            }
        }
    }
}

export function fetchFreeTopicDetailsOfDyad(dyadId: string): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if (state.auth.jwt != null && state.dyads.isLoadingFreeTopics === false) {
            dispatch(dyadsSlice.actions._setLoadingFreeTopicsFlag(true))
            try {
                const resp = await Http.axios.get(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_FREE_TOPICS, { dyad_id: dyadId }), {
                    headers: await Http.getSignedInHeaders(state.auth.jwt)
                })
                if (resp.status == 200) {
                    if (resp.data.dyad_id === dyadId) {
                        console.log(resp.data)
                        dispatch(dyadsSlice.actions._setFreeTopicDetails(resp.data))
                    }
                }
            } catch (ex) {
                console.log(ex)
            } finally {
                dispatch(dyadsSlice.actions._setLoadingFreeTopicsFlag(false))
            }
        }
    }
}

export function removeFreeTopicDetailById(dyadId: string, detailId: string): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if (state.auth.jwt != null) {
            dispatch(dyadsSlice.actions._setUpdatingFreeTopicsFlag(true))
            try {
                const resp = await Http.axios.delete(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_FREE_TOPICS_ID, { dyad_id: dyadId, detail_id: detailId }), {
                    headers: await Http.getSignedInHeaders(state.auth.jwt)
                })
                if (resp.status == 200) {
                    dispatch(dyadsSlice.actions._removeFreeTopicById(detailId))
                }
            } catch (ex) {
                console.log(ex)
            } finally {
                dispatch(dyadsSlice.actions._setUpdatingFreeTopicsFlag(false))
            }
        }
    }
}

export function updateFreeTopicDetail(dyadId: string, detailId: string, formData: FormData, onSuccess?: () => void): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if (state.auth.jwt != null) {
            dispatch(dyadsSlice.actions._setUpdatingFreeTopicsFlag(true))
            try {
                const resp = await Http.axios.putForm(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_FREE_TOPICS_ID, { dyad_id: dyadId, detail_id: detailId }), formData, {
                    headers: {
                        ...(await Http.getSignedInHeaders(state.auth.jwt)),
                        "Content-Type": 'multipart/form-data'
                    }
                })
                dispatch(dyadsSlice.actions._setOneFreeTopicDetail(resp.data))
                onSuccess?.()
            } catch (ex) {
                console.log(ex)
            }
        }
    }
}

export function createFreeTopicDetail(dyadId:string, formData: FormData, onSuccess?: () => void): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if (state.auth.jwt != null) {
            dispatch(dyadsSlice.actions._setUpdatingFreeTopicsFlag(true))
            try {
                const resp = await Http.axios.postForm(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_FREE_TOPICS, {dyad_id: dyadId}), formData, {
                    headers: {
                        ...(await Http.getSignedInHeaders(state.auth.jwt)),
                        "Content-Type": 'multipart/form-data'
                    }
                })
                dispatch(dyadsSlice.actions._addOneFreeTopicDetail(resp.data))
                onSuccess?.()
            } catch (ex) {
                console.log(ex)
            } finally{
                dispatch(dyadsSlice.actions._setUpdatingFreeTopicsFlag(false))
            }
        }
    }
}

export function fetchSessionSummariesOfDyad(dyadId: string): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if (state.auth.jwt != null && state.dyads.isLoadingSessionSummaries === false) {
            dispatch(dyadsSlice.actions._setLoadingSessionSummariesFlag(true))
            try {
                const resp = await Http.axios.get(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_SESSIONS, { dyad_id: dyadId }), {
                    headers: await Http.getSignedInHeaders(state.auth.jwt)
                })
                if (resp.status == 200) {
                    dispatch(dyadsSlice.actions._setSessionSummaries(resp.data))
                }
            } catch (ex) {
                console.log(ex)
            } finally {
                dispatch(dyadsSlice.actions._setLoadingSessionSummariesFlag(false))
            }
        }
    }
}


export function fetchDialogueOfSession(dyadId: string, sessionId: string): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if (state.auth.jwt != null && state.dyads.isLoadingDialogue === false) {
            dispatch(dyadsSlice.actions._setLoadingDialogueFlag(true))
            try {
                const resp = await Http.axios.get(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_DIALOGUE_ID, { dyad_id: dyadId, session_id: sessionId }), {
                    headers: await Http.getSignedInHeaders(state.auth.jwt)
                })
                if (resp.status == 200) {
                    dispatch(dyadsSlice.actions._setDialogue(resp.data))
                }
            } catch (ex) {
                console.log(ex)
            } finally {
                dispatch(dyadsSlice.actions._setLoadingDialogueFlag(false))
            }
        }
    }
}

export function fetchUserDefinedCards(dyadId: string): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if (state.auth.jwt != null && state.dyads.isLoadingDialogue === false) {
            dispatch(dyadsSlice.actions._setLoadingUserDefinedCardsFlag(true))
            try {
                const resp = await Http.axios.get(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_CUSTOM_CARDS, { dyad_id: dyadId }), {
                    headers: await Http.getSignedInHeaders(state.auth.jwt)
                })
                if (resp.status == 200) {
                    dispatch(dyadsSlice.actions._setUserDefinedCards(resp.data))
                }
            } catch (ex) {
                console.log(ex)
            } finally {
                dispatch(dyadsSlice.actions._setLoadingUserDefinedCardsFlag(false))
            }
        }
    }
}

export function createUserDefinedCard(dyadId:string, formData: FormData, onSuccess?: () => void): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if (state.auth.jwt != null) {
            dispatch(dyadsSlice.actions._setLoadingUserDefinedCardsFlag(true))
            try {
                const resp = await Http.axios.postForm(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_CUSTOM_CARDS_NEW, {dyad_id: dyadId}), formData, {
                    headers: {
                        ...(await Http.getSignedInHeaders(state.auth.jwt)),
                        "Content-Type": 'multipart/form-data'
                    }
                })
                dispatch(dyadsSlice.actions._addOneUserDefinedCard(resp.data))
                onSuccess?.()
            } catch (ex) {
                console.log(ex)
            } finally{
                dispatch(dyadsSlice.actions._setLoadingUserDefinedCardsFlag(false))
            }
        }
    }
}

export function removeUserDefinedCard(dyadId: string, cardId: string): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if (state.auth.jwt != null) {
            dispatch(dyadsSlice.actions._setLoadingUserDefinedCardsFlag(true))
            try {
                const resp = await Http.axios.delete(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_CUSTOM_CARDS_ID, { dyad_id: dyadId, card_id: cardId }), {
                    headers: await Http.getSignedInHeaders(state.auth.jwt)
                })
                if (resp.status == 200) {
                    dispatch(dyadsSlice.actions._removeUserDefinedCardById(cardId))
                }
            } catch (ex) {
                console.log(ex)
            } finally {
                dispatch(dyadsSlice.actions._setLoadingUserDefinedCardsFlag(false))
            }
        }
    }
}

export function deleteUserSession(dyadId: string, sessionId: string): AdminCoreThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if (state.auth.jwt != null) {
            try {
                const resp = await Http.axios.delete(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_SESSIONS_ID, {dyad_id: dyadId, session_id: sessionId}), {
                    headers: await Http.getSignedInHeaders(state.auth.jwt)
                })
                if (resp.status == 200){
                    dispatch(dyadsSlice.actions._removeSessionSummary(sessionId))
                }
            }catch(ex){
                console.log(ex)
            }
        }
    }
}

export const { clearDyadChildrenEntities } = dyadsSlice.actions

export default dyadsSlice.reducer
