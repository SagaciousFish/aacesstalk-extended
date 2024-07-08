import { CardInfo, DialogueRole, SessionStatus, TopicCategory, adminDialogueSelectors, adminSessionSummarySelectors, fetchDialogueOfSession, fetchSessionSummariesOfDyad } from "@aacesstalk/libs/ts-core"
import { useDispatch, useSelector } from "../../../redux/hooks"
import { useEffect, useMemo } from "react"
import { useDyadId } from "../hooks"
import {Button, Collapse, CollapseProps, Timeline} from 'antd'
import moment from 'moment-timezone'

const SessionElement = (props: {sessionId: string}) => {

    const dispatch = useDispatch()
    const dyadId = useDyadId()

    const dialogue = useSelector(state => adminDialogueSelectors.selectById(state, props.sessionId))

    const timelineData = useMemo(()=>{
        if(dialogue != null){
            return dialogue.dialogue.map(message => {

                let content

                switch(message.role){
                    case DialogueRole.Parent:
                        content = <span>{message.content_localized || message.content as any}</span>
                        break
                    case DialogueRole.Child:
                        const cards = (message.content as Array<CardInfo>)
                        content = <span>{cards.map((card, i) => <><span className="ml-1.5 bg-slate-200 p-1 rounded-md">{card.label_localized}</span>{i < cards.length-1 ? <span>,</span> : null}</>)}</span>
                }

                return {color: message.role == DialogueRole.Parent ? 'blue' : 'green', children: <div><span className="font-bold">{message.role == DialogueRole.Parent ? "부모": "자녀"}:</span> {content}</div>}
            })
        }
    }, [dialogue])

    useEffect(()=>{
        if(dyadId != null){
            dispatch(fetchDialogueOfSession(dyadId, props.sessionId))
        }

        return () => {
        }
    }, [dyadId, props.sessionId])

    return <Timeline items={timelineData}/>
}

export const DyadSessionsPage = () => {

    const dispatch = useDispatch()

    const dyadId = useDyadId()

    const sessions = useSelector(adminSessionSummarySelectors.selectAll)

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

    useEffect(()=>{
        if(dyadId != null){
            dispatch(fetchSessionSummariesOfDyad(dyadId))
        }
    }, [dyadId])

    return <Collapse className="m-6" items={collapsableItems} destroyInactivePanel/>
}