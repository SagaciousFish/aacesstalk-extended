import { useCallback, useEffect, useState } from "react"
import { useDispatch, useSelector } from "../../../redux/hooks";
import { Http, adminFreeTopicDetailsSelectors, fetchFreeTopicDetailsOfDyad, removeFreeTopicDetailById } from "@aacesstalk/libs/ts-core";
import { useMatch } from "react-router-dom";
import { Button, Card } from "antd";
import { PencilIcon, TrashIcon } from '@heroicons/react/24/solid'
import { FreeTopicModal } from "../components/FreeTopicModal";

const FreeTopicDetailElement = (props: { id: string, dyadId: string, onEditClick?: (id: string) => void }) => {

    const dispatch = useDispatch()

    const detail = useSelector(state => adminFreeTopicDetailsSelectors.selectById(state, props.id))

    const token = useSelector(state => state.auth.jwt)

    const onRemoveClick = useCallback(() => {
        if (window.confirm("Remove this free topic?")) {
            dispatch(removeFreeTopicDetailById(props.dyadId, props.id))
        }
    }, [props.dyadId, props.id])

    const [imageSource, setImageSource] = useState<null | string>(null)

    useEffect(() => {
        if (props.dyadId != null && props.id != null && token != null && detail?.topic_image_filename != null) {
            const loadImage = async () => {
                try {
                    const response = await Http.axios.get(Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_FREE_TOPICS_IMAGE, { dyad_id: props.dyadId, detail_id: props.id }), {
                        headers: await Http.getSignedInHeaders(token),
                    })
                    const b64 = Buffer.from(response.data, 'binary').toString('base64')
                } catch (ex) {
                    console.log("Image loading error")
                }
            }
            loadImage().then()
        }
    }, [props.dyadId, props.id, token, detail?.topic_image_filename])

    const onEditClick = useCallback(() => {
        props.onEditClick?.(props.id)
    }, [props.onEditClick, props.id])

    return <Card size="small"
        rootClassName="border-orange-300 border-2 shadow-md flex-1"
        className="p-0"
        title={<span className="font-bold text-md">{detail?.subtopic}</span>}
        extra={<div className="flex text-gray-600">
            <Button type="text" className="p-2" onClick={onEditClick}><PencilIcon className="w-5 h-5" key="edit" /></Button>
            <Button type="text" className="p-2" onClick={onRemoveClick}><TrashIcon className="w-5 h-5 text-red-400" key="delete" /></Button>
        </div>}
    >
        {detail?.topic_image_filename == null ? <div className="aspect-square bg-slate-50 mb-3 flex items-center justify-center"><span className="text-gray-400">No images assigned.</span></div> : null}
        <p className="">{detail?.subtopic_description}</p>
    </Card>
}

export const FreeTopicSettingsPage = () => {

    const dispatch = useDispatch()

    const currentMountedDyadId = useSelector(state => state.dyads.mountedDyadId)

    const topicIds = useSelector(adminFreeTopicDetailsSelectors.selectIds)

    const urlMatch = useMatch("/dyads/:dyadId/*")
    const routeDyadId = urlMatch?.params.dyadId

    const [topicIdToEdit, setTopicIdToEdit] = useState<string|undefined>(undefined)
    const [isModalOpen, setIsModalOpen] = useState(false)

    useEffect(() => {
        if (routeDyadId != null) {
            dispatch(fetchFreeTopicDetailsOfDyad(routeDyadId))
        }
    }, [routeDyadId])

    const onEditClick = useCallback((id: string) => {
        setTopicIdToEdit(id)
        setIsModalOpen(true)
    }, [])

    const onAddNewClick = useCallback(()=>{
        setTopicIdToEdit(undefined)
        setIsModalOpen(true)
    }, [])

    const onModalCloseRequested = useCallback(()=>{
        setIsModalOpen(false)
    }, [])

    return routeDyadId != null && currentMountedDyadId == routeDyadId ? <div>{(topicIds.length > 0 ? <div className="grid grid-cols-3 gap-8 m-10">
        {
            topicIds.map(id => <FreeTopicDetailElement key={id} id={id} dyadId={routeDyadId} onEditClick={onEditClick} />)
        }
    </div> : <div className="p-10">No free topics defined.</div>)} <Button rootClassName="ml-10" onClick={onAddNewClick}>Add New Topic</Button>
        <FreeTopicModal topicId={topicIdToEdit} open={isModalOpen} onCancel={onModalCloseRequested} onClose={onModalCloseRequested}/>
    </div> : null
}