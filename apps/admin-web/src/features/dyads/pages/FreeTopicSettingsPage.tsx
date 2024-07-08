import { useCallback, useEffect, useMemo, useState } from "react"
import { useDispatch, useSelector } from "../../../redux/hooks";
import { Http, adminFreeTopicDetailsSelectors, fetchFreeTopicDetailsOfDyad, removeFreeTopicDetailById } from "@aacesstalk/libs/ts-core";
import { useMatch } from "react-router-dom";
import { Button, Card, Image } from "antd";
import { PencilIcon, TrashIcon } from '@heroicons/react/24/solid'
import { FreeTopicModal } from "../components/FreeTopicModal";
import { useNetworkImageSource } from "../hooks";
import Meta from "antd/es/card/Meta";

const FreeTopicDetailElement = (props: { id: string, dyadId: string, onEditClick?: (id: string) => void }) => {

    const dispatch = useDispatch()

    const detail = useSelector(state => adminFreeTopicDetailsSelectors.selectById(state, props.id))

    const onRemoveClick = useCallback(() => {
        if (window.confirm("Remove this free topic?")) {
            dispatch(removeFreeTopicDetailById(props.dyadId, props.id))
        }
    }, [props.dyadId, props.id])

    const imageSource = useNetworkImageSource(
        useMemo(()=>Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_FREE_TOPICS_IMAGE, { dyad_id: props.dyadId, detail_id: props.id }), [props.dyadId, props.id]),
        detail?.topic_image_filename
    )

    const onEditClick = useCallback(() => {
        props.onEditClick?.(props.id)
    }, [props.onEditClick, props.id])

    return <Card size="small"
        rootClassName="shadow-md flex-1"
        className="p-0"
        actions={[<Button type="text" className="p-2" onClick={onEditClick}><PencilIcon className="w-4 h-4" key="edit" /></Button>,
        <Button type="text" className="p-2" onClick={onRemoveClick}><TrashIcon className="w-4 h-4 text-red-400" key="delete" /></Button>
        ]}
        cover={detail?.topic_image_filename == null ? <div className="aspect-square bg-slate-50 mb-3 flex items-center justify-center"><span className="text-gray-400">No images assigned.</span></div> : <Image src={imageSource!}/>}
    >
        <Meta title={<span className="font-bold text-md">{detail?.subtopic}</span>} description={detail?.subtopic_description}/>
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

    return routeDyadId != null && currentMountedDyadId == routeDyadId ? <div>{(topicIds.length > 0 ? <div className="grid grid-cols-4 gap-8 m-10">
        {
            topicIds.map(id => <FreeTopicDetailElement key={id} id={id} dyadId={routeDyadId} onEditClick={onEditClick} />)
        }
    </div> : <div className="p-10">No free topics defined.</div>)} <Button rootClassName="ml-10" onClick={onAddNewClick}>Add New Topic</Button>
        <FreeTopicModal dyadId={routeDyadId} topicId={topicIdToEdit} open={isModalOpen} onCancel={onModalCloseRequested} onClose={onModalCloseRequested}/>
    </div> : null
}