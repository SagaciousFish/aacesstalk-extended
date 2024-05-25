import axios, { Axios, CreateAxiosDefaults } from 'axios';
import format = require('string-template');

const DEFAULTS: CreateAxiosDefaults<any> = {
  baseURL: "/api/v1"
}

export class Http{

  static ENDPOINT_DYAD = "/dyad"
  static ENDPOINT_DYAD_ACCOUNT = `${Http.ENDPOINT_DYAD}/account`

  static ENDPOINT_DYAD_ACCOUNT_LOGIN = `${Http.ENDPOINT_DYAD_ACCOUNT}/login`

  static ENDPOINT_DYAD_SESSION = `${Http.ENDPOINT_DYAD}/session`
  static ENDPOINT_DYAD_SESSION_NEW = `${Http.ENDPOINT_DYAD_SESSION}/new`

  static ENDPOINT_DYAD_SESSION_ID = `${Http.ENDPOINT_DYAD_SESSION}/{session_id}`

  static ENDPOINT_DYAD_SESSION_END = `${Http.ENDPOINT_DYAD_SESSION_ID}/end`

  static ENDPOINT_DYAD_SESSION_ABORT = `${Http.ENDPOINT_DYAD_SESSION_ID}/abort`
  static ENDPOINT_DYAD_MESSAGE = `${Http.ENDPOINT_DYAD_SESSION_ID}/message`

  static getTemplateEndpoint(template: string, values: {[key:string]: string}): string {
    return format(template, values)
  }

  private static axiosInstance: Axios = axios.create({
    ...DEFAULTS
  })

  private static getTimezone: () => Promise<string>
  private static isInitialized = false

  static get axios(): Axios {
    return this.axiosInstance
  }

  static async getDefaultHeaders(): Promise<any> {
    if(!this.isInitialized){
      throw Error("Http.initialize() has not been called.")
    }

    return {
      "Timezone": await this.getTimezone()
    }
  }

  static async getSignedInHeaders(token: string): Promise<any> {
    return {
      ...await this.getDefaultHeaders(),
      "Authorization": `Bearer ${token}`
    }
  }

  static initialize(getTimezone: () => Promise<string>){
    Http.getTimezone = getTimezone
    Http.isInitialized = true
  }
}
