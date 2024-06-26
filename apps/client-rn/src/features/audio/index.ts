import { useCallback, useEffect, useRef } from "react";
import Recorder, { AudioEncoderAndroidType, AudioSet, AudioSourceAndroidType, OutputFormatAndroidType } from 'react-native-audio-recorder-player'
import { FileSystem } from 'react-native-file-access';

const DEFAULT_AUDIO_SETTINGS: AudioSet = {
    AudioEncoderAndroid: AudioEncoderAndroidType.AAC,
    AudioSourceAndroid: AudioSourceAndroidType.MIC,
    OutputFormatAndroid: OutputFormatAndroidType.MPEG_4
}

export function useAudioRecord(){
    const recorder = useRef<Recorder>()
    const isRecordingActive = useRef<boolean>(false)

    const startRecording = useCallback(async (filePath: string, settings?: AudioSet): Promise<string|null> => {
        if(isRecordingActive.current == false){
            isRecordingActive.current = true
            return await recorder.current.startRecorder(filePath, settings || DEFAULT_AUDIO_SETTINGS)
        }else{
            return null
        }
    }, [])

    const pauseRecording = useCallback(async () => {
        if(isRecordingActive.current == true){
            return await recorder.current.pauseRecorder()
        }
    }, [])

    const resumeRecording = useCallback(async () => {
        if(isRecordingActive.current == true){
            return await recorder.current.resumeRecorder()
        }
    }, [])

    const stopRecording = useCallback(async () => {
        if(isRecordingActive.current == true){
            return await recorder.current.stopRecorder()
        }
    }, [])

    useEffect(()=>{
        recorder.current = new Recorder()

        return () => {
            if(isRecordingActive.current === true){
                recorder.current.stopRecorder().then((uri: string) => {
                    // Handle file removal
                    return FileSystem.unlink(uri)
                }).then(()=>{
                    console.log("Removed unused audio file.")
                }).catch(ex => {
                    console.log(ex)
                }).finally(()=>{
                    recorder.current.removeRecordBackListener()
                    recorder.current = null
                })
            }
        }
    }, [])

    return {
        startRecording,
        pauseRecording,
        resumeRecording,
        stopRecording
    }
}