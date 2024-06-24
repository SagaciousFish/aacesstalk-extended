import { CardImageMatching, Http } from "@aacesstalk/libs/ts-core"
import { Subject, Subscription, filter, map } from "rxjs"

export class CardImageManager{
    private static _instance: CardImageManager | undefined = undefined

    static get instance(): CardImageManager {
        if(this._instance == null){
            this._instance = new CardImageManager()
        }

        return this._instance
    }

    private readonly cardImageMatchingDict: Map<string, CardImageMatching>

    private readonly eventSubject: Subject<{id: string, matching: CardImageMatching}>

    private constructor(){
        this.cardImageMatchingDict = new Map()
        this.eventSubject = new Subject()
    }

    getCachedMatching(cardInfoId: string): CardImageMatching | null {
        if(this.cardImageMatchingDict.has(cardInfoId)){
            return this.cardImageMatchingDict.get(cardInfoId)
        }else{
            return null
        }
    }

    subscribeToImageMatching(cardInfoId: string, callback: ((matching: CardImageMatching)=>void) | ((matching: CardImageMatching)=>Promise<void>)): Subscription {
        return this.eventSubject.pipe(filter(event => event.id === cardInfoId), map(event => event.matching)).subscribe(callback)
    }

    registerImageMatchingTask(recommendationId: string, token: string): {cancel:()=>void}{
        let controller = new AbortController()
        
        Http.getSignedInHeaders(token).then(headers => {
            Http.axios.get(Http.ENDPOINT_DYAD_MEDIA_MATCH_CARD_IMAGES + "/" + recommendationId, {
                headers,
                signal: controller.signal
            }).then(
                result => {
                    const matchings: Array<CardImageMatching> = result.data.matchings
                    console.log("Card image matching result received.", matchings.length)
                    for(const match of matchings){
                        if(this.cardImageMatchingDict.has(match.card_info_id) == false){
                            this.cardImageMatchingDict.set(match.card_info_id, match)
                            this.eventSubject.next({id: match.card_info_id, matching: match})
                        }
                    }
                }
            ).catch((err) => {
                console.log(err)
            }).finally(()=>{
                controller = null
            })
        })
        
        
        return {
            cancel:()=>{
                console.log("controller: ", controller)
                controller?.abort()
            }
        }
    }
}