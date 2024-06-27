import { PayloadAction, createSlice } from "@reduxjs/toolkit";
import { AudioEncoderAndroidType, AudioSet, AudioSourceAndroidType, OutputFormatAndroidType } from 'react-native-audio-recorder-player'
import { Lazy } from "../../utils/lazy";
import AudioRecorderPlayer, { RecordBackType } from "react-native-audio-recorder-player";
import { ClientThunk } from "../../redux/store";
import { Dirs, FileSystem } from "react-native-file-access";


export enum RecordingStatus{
    Initial="initial",
    Preparing="preparing",
    Recording="recording",
    RecordingPause="recording-pause",
    Stopping="stopping"
}

export interface ParentAudioRecordingState{
    status: RecordingStatus
    recordingStartedTimestamp?: number,
    recordingDurationMillis: number,
    recordingMeter?: number
}

const INITIAL_STATE: ParentAudioRecordingState = {
    status: RecordingStatus.Initial,
    recordingMeter: undefined,
    recordingDurationMillis: 0,
    recordingStartedTimestamp: undefined
}

const parentAudioRecordingSlice = createSlice({
    name: 'parentAudioRecording',
    initialState: INITIAL_STATE,
    reducers: {
        setRecordingStatus:(state, action: PayloadAction<RecordingStatus>) => {
            state.status = action.payload
            if(action.payload == RecordingStatus.Stopping || action.payload == RecordingStatus.Initial){
                state.recordingMeter = undefined
            }
        },
        setRecordingStartTimestamp: (state, action: PayloadAction<number|undefined>) => {
            state.recordingStartedTimestamp = action.payload
        }, 

        setRecordingArgs: (state, action: PayloadAction<RecordBackType>) => {
            state.recordingMeter = action.payload.currentMetering
            state.recordingDurationMillis = action.payload.currentPosition
        }
    }
})

export default parentAudioRecordingSlice.reducer


const DEFAULT_AUDIO_SETTINGS: AudioSet = {
    AudioEncoderAndroid: AudioEncoderAndroidType.AAC,
    AudioSourceAndroid: AudioSourceAndroidType.MIC,
    OutputFormatAndroid: OutputFormatAndroidType.MPEG_4,
}

const recorder = new Lazy(() => {
    const player = new AudioRecorderPlayer()
    player.setSubscriptionDuration(0.1)
    return player
} )
let isRecordingActive = false

export function startRecording(recordingStartedTimestamp: number = Date.now()): ClientThunk {
    return async (dispatch, getState) => {
        const state = getState()
        const sessionId = state.session.id
        console.log("session id: ", sessionId, state.session)
        const parentTurnOrder = Math.floor(state.session.numTurns/2)
        const audioDirPath = Dirs.CacheDir + "/audio_recording"
        if(await FileSystem.exists(audioDirPath) == false){
            await FileSystem.mkdir(audioDirPath)
        }
        const audioFilePath = audioDirPath + `/${sessionId}_${parentTurnOrder}.m4a`

        if(isRecordingActive == false && state.parentAudioRecording.status == RecordingStatus.Initial){
            console.log("Recording started.")
            isRecordingActive = true
            dispatch(parentAudioRecordingSlice.actions.setRecordingStatus(RecordingStatus.Preparing))
            recorder.get().addRecordBackListener((args) => {
                dispatch(parentAudioRecordingSlice.actions.setRecordingArgs(args))
            })
            await recorder.get().startRecorder( audioFilePath , DEFAULT_AUDIO_SETTINGS, true)
            dispatch(parentAudioRecordingSlice.actions.setRecordingStartTimestamp(recordingStartedTimestamp))
            dispatch(parentAudioRecordingSlice.actions.setRecordingStatus(RecordingStatus.Recording))
        }
    }
}

export function pauseRecording(): ClientThunk {
    return async (dispatch, getState) => {
        const state = getState()
        if(isRecordingActive == true && state.parentAudioRecording.status == RecordingStatus.Recording){
            await recorder.get().pauseRecorder()
            dispatch(parentAudioRecordingSlice.actions.setRecordingStatus(RecordingStatus.RecordingPause))
        }
    }
}

export function resumeRecording(){
    return async (dispatch, getState) => {
        const state = getState()
        if(isRecordingActive == true && state.parentAudioRecording.status == RecordingStatus.RecordingPause){
            await recorder.get().resumeRecorder()
            dispatch(parentAudioRecordingSlice.actions.setRecordingStatus(RecordingStatus.Recording))
        }
    }
}

export function stopRecording(cancel: boolean = false): ClientThunk{
    return async (dispatch, getState) => {
        const state = getState()
        if(isRecordingActive == true && (state.parentAudioRecording.status == RecordingStatus.RecordingPause || state.parentAudioRecording.status == RecordingStatus.Recording)){
            console.log("Recording stopped.")
            isRecordingActive = false
            dispatch(parentAudioRecordingSlice.actions.setRecordingStatus(RecordingStatus.Stopping))
            const uri = await recorder.get().stopRecorder()
            recorder.get().removeRecordBackListener()
            console.log("audio file recorded at: ", uri)
            if(cancel){
                console.log("recording was canceled. remove audio file")
                if(await FileSystem.exists(uri)){
                    await FileSystem.unlink(uri)
                }
            }
            dispatch(parentAudioRecordingSlice.actions.setRecordingStatus(RecordingStatus.Initial))
        }
    }
}