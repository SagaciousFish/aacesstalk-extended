import { CardInfo, DialogueRole, Http, ParentGuideType, SessionStatus, TopicCategory, adminDialogueSelectors, adminSessionSummarySelectors, fetchDialogueOfSession, fetchSessionSummariesOfDyad } from "@aacesstalk/libs/ts-core"
import { useDispatch, useSelector } from "../../../redux/hooks"
import { useCallback, useEffect, useMemo, useState } from "react"
import { useDyadId } from "../hooks"
import {Button, Card, Collapse, CollapseProps, List, Space, Switch, Timeline, Typography} from 'antd'
import moment from 'moment-timezone'
import { SwitchChangeEventHandler } from "antd/es/switch"
import AudioPlayer from 'react-h5-audio-player';
import 'react-h5-audio-player/lib/styles.css';
import FileSaver from 'file-saver'

const TurnAudioPlayer = (props: {sessionId: string, turnId: string}) => {

    const dyadId = useDyadId()

    const [audioBlobUrl, setAudioBlobUrl] = useState<string|undefined>(undefined)

    const token = useSelector(state => state.auth.jwt)

    const mountAudioFile = useCallback(async () => {
        if(dyadId != null && props.sessionId != null && props.turnId != null && token != null){
            const url = Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_DIALOGUE_ID_AUDIO, {
                session_id: props.sessionId,
                turn_id: props.turnId,
                dyad_id: dyadId
            })
            try{
                const result = await Http.axios.get(url, {
                    headers: {...await Http.getSignedInHeaders(token), 
                        'Content-Type': 'audio/*'},
                    responseType: 'blob'
                })
                setAudioBlobUrl(URL.createObjectURL(result.data))
            }catch(ex){
                console.log(ex)
            }
        }
    }, [token, dyadId, props.sessionId, props.turnId
    ])

    useEffect(() => {
        return function cleanup() {
            if (audioBlobUrl != null) {
                URL.revokeObjectURL(audioBlobUrl)
            }
        }
    })

    return audioBlobUrl != null ? <AudioPlayer className="ml-2" src={audioBlobUrl} autoPlay/> : <Button className="ml-2" size="small" onClick={mountAudioFile}>Play recording</Button>
}

const SessionElement = (props: {sessionId: string}) => {

    const dispatch = useDispatch()
    const dyadId = useDyadId()

    const dialogue = useSelector(state => adminDialogueSelectors.selectById(state, props.sessionId))

    const [isRichMode, setRichMode] = useState(false)

    const extendedSwitchHandler = useCallback<SwitchChangeEventHandler>((checked) => {
        setRichMode(checked)
    }, [])

    const timelineData = useMemo(()=>{
        if(dialogue != null){
            return dialogue.dialogue.map(message => {

                let content

                switch(message.role){
                    case DialogueRole.Parent:
                        content = <div>
                                <span>{message.content_localized || message.content as any}</span>
                                {
                                    isRichMode === true ? <><TurnAudioPlayer sessionId={props.sessionId} turnId={message.turn_id!}/>
                                        <List size="small" dataSource={message.guides} renderItem={(item, index) => {
                                            return <List.Item className="flex">
                                                <div className="w-28">
                                                    <Typography.Text code className="text-xs">{item.category}</Typography.Text>
                                                </div>
                                                <div className={`w-80 ${item.type == ParentGuideType.Feedback ? "bg-red-100" : ""}`}>{Array.isArray(item.guide_localized) ? item.guide_localized.join(", ") : item.guide_localized}<br/><span className="text-[#aaa]">({item.guide})</span></div>
                                                <div className="flex-1">{
                                                    item.type == ParentGuideType.Messaging ? <>
                                                        <span className="italic">"{item.example_localized}"</span> <span className={`ml-1 px-1 text-xs ${item.example_accessed === true? "bg-green-300":'bg-red-200'} rounded-md`}>{item.example_accessed === true ? "Accessed" : "Not Accessed"}</span>
                                                        <br/>
                                                        <span className="text-[#aaa]">({item.example})</span>
                                                    </> : null
                                                }</div>
                                            </List.Item>
                                        }}/>
                                    </> : null
                                }
                            </div>
                        break
                    case DialogueRole.Child:
                        const cards = (message.content as Array<CardInfo>)
                        content = <div className="ml-[-5px]">{cards.map((card, i) => <><span className="ml-1.5 bg-slate-200 p-1 rounded-md">{card.label_localized}</span>{i < cards.length-1 ? <span>,</span> : null}</>)}</div>
                }

                return {color: message.role == DialogueRole.Parent ? 'blue' : 'green', children: <div className="flex flex-row items-baseline"><span className="font-bold mr-2">{message.role == DialogueRole.Parent ? "부모": "자녀"}:</span> {content}</div>}
            })
        }
    }, [dialogue, isRichMode])

    useEffect(()=>{
        if(dyadId != null){
            dispatch(fetchDialogueOfSession(dyadId, props.sessionId))
        }

        return () => {
        }
    }, [dyadId, props.sessionId])

    return <div>
            <div className="flex flex-row items-center mb-5">
                <Switch id={`switch_${props.sessionId}`} title="Extended" value={isRichMode} onChange={extendedSwitchHandler} size="small"/>
                <label htmlFor={`switch_${props.sessionId}`} className="ml-2">Rich content mode</label>
            </div>
            <Timeline items={timelineData}/>
        </div>
}

export const DyadSessionsPage = () => {

    const dispatch = useDispatch()

    const dyadId = useDyadId()

    const sessions = useSelector(adminSessionSummarySelectors.selectAll)

    const token = useSelector(state => state.auth.jwt)

    const collapsableItems: CollapseProps['items'] = useMemo(()=>{
        return sessions.map(session => {

            const m = moment.tz(session.started_timestamp, session.local_timezone)
            const dateString = m.format("YYYY-MM-DD")
            const timeString = m.format("hh:mm:ss A")

            let topicColor: string
            switch(session.topic.category){
                case TopicCategory.Free:
                    topicColor = "bg-orange-300"
                    break
                case TopicCategory.Plan:
                    topicColor = "bg-blue-400"
                    break
                case TopicCategory.Recall:
                    topicColor = "bg-green-400"
                    break
            }

            let topicString: string = session.topic.category
            if(session.topic.subtopic != null){
                topicString = `${topicString} (${session.topic.subtopic})`
            }

            return {
                key: session.id,
                label: <div className="flex">
                        <div className="w-[25%]">
                            <span className="bg-slate-300 p-1 px-1.5 rounded-md mr-2">{dateString}</span><span>{timeString}</span>
                        </div>
                        <div className="w-[15%]">
                            <span className={`${topicColor} p-1 px-1.5 rounded-md capitalize`}>{topicString}</span>
                        </div>
                        <div className="w-[12%]">
                            <span className={`${session.status == SessionStatus.Conversation ? "text-red-400" : "text-slate-600"} capitalize font-semibold`}>{session.status}</span>
                        </div>
                        <div className="w-[25%]">
                            <span className={`text-sm`}>{session.num_turns} turn(s)</span>
                        </div>
                    </div>,
                children: <SessionElement sessionId={session.id}/>,
                collapsible: session.num_turns === 0 ? 'disabled' : 'header'
            }
        })
    }, [sessions])    

    const onExportClick = useCallback(async ()=>{
        if(token != null && dyadId != null){
            try{
                const resp = await Http.axios.get(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DATA_DIALOGUES_ID,{dyad_id: dyadId}), {
                    headers: await Http.getSignedInHeaders(token),
                    responseType: 'blob'
                })
                FileSaver.saveAs(resp.data)

            }catch(ex){
                console.log(ex)
            }
        }
    }, [token, dyadId])

    useEffect(()=>{
        if(dyadId != null){
            dispatch(fetchSessionSummariesOfDyad(dyadId))
        }
    }, [dyadId])

    return <div className="p-6">
            <Button type="primary" className="mb-4" onClick={onExportClick}>Export Dataset</Button>
            {sessions.length > 0 ? <Collapse items={collapsableItems} destroyInactivePanel/> : <div>No sessions.</div>}
        </div>
}