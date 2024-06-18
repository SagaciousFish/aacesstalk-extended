import { CardIdentity, CardInfo, Http } from '@aacesstalk/libs/ts-core';
import { Dirs, FileSystem } from 'react-native-file-access';
import { ManagedFetchResult } from 'react-native-file-access/lib/typescript/types';
import SoundPlayer from 'react-native-sound-player'

export interface ManagedVoiceOverFetchTask{
    cancel: () => Promise<void>
}

export class VoiceOverManager {

    private static _instance: VoiceOverManager | undefined = undefined
    
    static get instance(): VoiceOverManager{
        if(this._instance == null){
            this._instance = new VoiceOverManager()
        }

        return this._instance
    }

    private fileFetchTaskMap = new Map<string, ManagedFetchResult>()

    private constructor(){}

    async cancelAll(){
        const tasks = Array.from(this.fileFetchTaskMap.values())
        await Promise.allSettled(tasks.map(t => t.cancel()))
        this.fileFetchTaskMap.clear()
        SoundPlayer.stop()
    }

    async placeVoiceoverFetchTask(cardInfo: CardInfo, authToken: string): Promise<ManagedVoiceOverFetchTask>{

        const headers = {
            ...(await Http.getSignedInHeaders(authToken)),
            'Content-Type': 'audio/mpeg'
        }

        const dir = Dirs.CacheDir + "/voiceover"
        if(await FileSystem.exists(dir) == false){
            await FileSystem.mkdir(dir)
        }

        const filePath = dir + `/voiceover_${cardInfo.id}.mp3`

        const task = FileSystem.fetchManaged( `${Http.axios.defaults.baseURL}${Http.ENDPOINT_DYAD_MEDIA_VOICEOVER}?card_id=${cardInfo.id}&recommendation_id=${cardInfo.recommendation_id}`, 
            {
                headers,
                method: 'GET',
                path: filePath
            })

        this.fileFetchTaskMap.set(cardInfo.id, task)

        const result = await task.result
        if(result.ok){
            console.log("Play audio...", filePath)
            SoundPlayer.playUrl("file://" + filePath)
        }else{
            console.log("Fail", result.statusText)
        }
        
        return {
            cancel: async () => {
                await task.cancel()
            }
        }
    }
}