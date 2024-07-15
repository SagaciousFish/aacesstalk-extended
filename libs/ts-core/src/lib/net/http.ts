import axios, { Axios, CreateAxiosDefaults } from 'axios';
import pupa from 'pupa'

export class Http{

  static ENDPOINT_PING = "/ping"

  static ENDPOINT_DYAD = "/dyad"
  static ENDPOINT_DYAD_ACCOUNT = `${Http.ENDPOINT_DYAD}/account`

  static ENDPOINT_DYAD_DATA = `${Http.ENDPOINT_DYAD}/data`

  static ENDPOINT_DYAD_ACCOUNT_LOGIN = `${Http.ENDPOINT_DYAD_ACCOUNT}/login`

  static ENDPOINT_DYAD_MEDIA = `${Http.ENDPOINT_DYAD}/media`

  static ENDPOINT_DYAD_DATA_FREE_TOPICS = `${Http.ENDPOINT_DYAD_DATA}/freetopics`

  static ENDPOINT_DYAD_SESSION = `${Http.ENDPOINT_DYAD}/session`
  static ENDPOINT_DYAD_SESSION_NEW = `${Http.ENDPOINT_DYAD_SESSION}/new`

  static ENDPOINT_DYAD_SESSION_LIST = `${Http.ENDPOINT_DYAD_SESSION}/list`

  static ENDPOINT_DYAD_SESSION_ID = `${Http.ENDPOINT_DYAD_SESSION}/{session_id}`


  static ENDPOINT_DYAD_SESSION_START = `${Http.ENDPOINT_DYAD_SESSION_ID}/start`

  static ENDPOINT_DYAD_SESSION_END = `${Http.ENDPOINT_DYAD_SESSION_ID}/end`

  static ENDPOINT_DYAD_SESSION_ABORT = `${Http.ENDPOINT_DYAD_SESSION_ID}/abort`
  static ENDPOINT_DYAD_MESSAGE = `${Http.ENDPOINT_DYAD_SESSION_ID}/message`

  static ENDPOINT_DYAD_MESSAGE_PARENT_GUIDE = `${Http.ENDPOINT_DYAD_MESSAGE}/parent/guide`
  static ENDPOINT_DYAD_MESSAGE_PARENT_SEND_MESSAGE_TEXT = `${Http.ENDPOINT_DYAD_MESSAGE}/parent/message/text`
  static ENDPOINT_DYAD_MESSAGE_PARENT_SEND_MESSAGE_AUDIO = `${Http.ENDPOINT_DYAD_MESSAGE}/parent/message/audio`
  static ENDPOINT_DYAD_MESSAGE_PARENT_EXAMPLE = `${Http.ENDPOINT_DYAD_MESSAGE}/parent/example`
  
  static ENDPOINT_DYAD_MESSAGE_CHILD_APPEND_CARD = `${Http.ENDPOINT_DYAD_MESSAGE}/child/add_card`
  static ENDPOINT_DYAD_MESSAGE_CHILD_REFRESH_CARDS = `${Http.ENDPOINT_DYAD_MESSAGE}/child/refresh_cards`
  static ENDPOINT_DYAD_MESSAGE_CHILD_CONFIRM_CARDS = `${Http.ENDPOINT_DYAD_MESSAGE}/child/confirm_cards`
  static ENDPOINT_DYAD_MESSAGE_CHILD_POP_LAST_CARD = `${Http.ENDPOINT_DYAD_MESSAGE}/child/pop_last_card`


  static ENDPOINT_DYAD_MEDIA_VOICEOVER = `${Http.ENDPOINT_DYAD_MEDIA}/voiceover`
  static ENDPOINT_DYAD_MEDIA_CARD_IMAGE = `${Http.ENDPOINT_DYAD_MEDIA}/card_image`
  static ENDPOINT_DYAD_MEDIA_MATCH_CARD_IMAGES = `${Http.ENDPOINT_DYAD_MEDIA}/match_card_images`

  static ENDPOINT_DYAD_MEDIA_FREE_TOPIC_IMAGE = `${Http.ENDPOINT_DYAD_MEDIA}/freetopic`

  // Admin endpoints ///////////////////////////////////////////////////////////////////////////////////////////////////

  static ENDPOINT_ADMIN = "/admin"

  static ENDPOINT_ADMIN_AUTH = `${Http.ENDPOINT_ADMIN}/auth`
  static ENDPOINT_ADMIN_ACCOUNT_LOGIN = `${Http.ENDPOINT_ADMIN_AUTH}/login`
  static ENDPOINT_ADMIN_ACCOUNT_VERIFY = `${Http.ENDPOINT_ADMIN_AUTH}/token`

  static ENDPOINT_ADMIN_DYADS = `${Http.ENDPOINT_ADMIN}/dyads`

  static ENDPOINT_ADMIN_DYADS_ALL = `${Http.ENDPOINT_ADMIN_DYADS}/all`

  static ENDPOINT_ADMIN_DYADS_NEW = `${Http.ENDPOINT_ADMIN_DYADS}/new`
  static ENDPOINT_ADMIN_DYADS_ID = `${Http.ENDPOINT_ADMIN_DYADS}/{dyad_id}`

  static ENDPOINT_ADMIN_DYADS_ID_FREE_TOPICS = `${Http.ENDPOINT_ADMIN_DYADS_ID}/freetopics`
  static ENDPOINT_ADMIN_DYADS_ID_FREE_TOPICS_ID = `${Http.ENDPOINT_ADMIN_DYADS_ID_FREE_TOPICS}/{detail_id}`
  static ENDPOINT_ADMIN_DYADS_ID_FREE_TOPICS_IMAGE = `${Http.ENDPOINT_ADMIN_DYADS_ID_FREE_TOPICS_ID}/image`

  static ENDPOINT_ADMIN_DYADS_ID_SESSIONS = `${Http.ENDPOINT_ADMIN_DYADS_ID}/sessions`
  static ENDPOINT_ADMIN_DYADS_ID_DIALOGUE_ID = `${Http.ENDPOINT_ADMIN_DYADS_ID}/dialogues/{session_id}`

  static ENDPOINT_ADMIN_DYADS_ID_DIALOGUE_ID_AUDIO = `${Http.ENDPOINT_ADMIN_DYADS_ID}/dialogues/{session_id}/{turn_id}/audio`


  static ENDPOINT_ADMIN_DYADS_ID_CUSTOM_CARDS = `${Http.ENDPOINT_ADMIN_DYADS_ID}/custom_cards`

  static ENDPOINT_ADMIN_DYADS_ID_CUSTOM_CARDS_NEW = `${Http.ENDPOINT_ADMIN_DYADS_ID_CUSTOM_CARDS}/new`

  static ENDPOINT_ADMIN_DYADS_ID_CUSTOM_CARDS_ID = `${Http.ENDPOINT_ADMIN_DYADS_ID}/custom_cards/{card_id}`  
  static ENDPOINT_ADMIN_DYADS_ID_CUSTOM_CARDS_ID_IMAGE = `${Http.ENDPOINT_ADMIN_DYADS_ID}/custom_cards/{card_id}/image`  




  static getTemplateEndpoint(template: string, values: {[key:string]: string}): string {
    return pupa(template, values)
  }

  private static axiosInstance: Axios

  private static _getTimezone: () => Promise<string>
  static getTimezone(): Promise<string>{
    return this._getTimezone()
  }
  private static isInitialized = false

  static get axios(): Axios {
    if(!this.isInitialized){
      throw Error("Http.initialize() has not been called.")
    }

    return this.axiosInstance
  }

  static async getDefaultHeaders(): Promise<any> {
    if(!this.isInitialized){
      throw Error("Http.initialize() has not been called.")
    }

    return {
      "Timezone": await this.getTimezone(),
      "Timestamp": Date.now().toString()
    }
  }

  static async getSignedInHeaders(token: string): Promise<any> {
    return {
      ...await this.getDefaultHeaders(),
      "Authorization": `Bearer ${token}`
    }
  }

  static initialize(backendAddress: string, getTimezone: () => Promise<string>){
    Http._getTimezone = getTimezone

    this.axiosInstance = axios.create({
      baseURL: `${backendAddress}/api/v1`
    })

    Http.isInitialized = true
  }
}
