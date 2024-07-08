import { useCallback, useEffect, useMemo, useState } from "react"
import { useDispatch, useSelector } from "../../../redux/hooks"
import { Http, fetchUserDefinedCards, removeUserDefinedCard, userDefinedCardSelectors } from "@aacesstalk/libs/ts-core"
import { useDyadId, useNetworkImageSource } from "../hooks"
import { Button, Card, Image } from "antd"
import { CustomCardModal } from "../components/CustomCardModal"
import { TrashIcon } from '@heroicons/react/24/solid'

const CustomCardElement = (props: {id: string}) => {
    const dispatch = useDispatch()

    const cardInfo = useSelector(state => userDefinedCardSelectors.selectById(state, props.id))

    const dyadId = useDyadId()


    const imageSource = useNetworkImageSource(
        useMemo(()=>dyadId != null ? Http.getTemplateEndpoint(Http.ENDPOINT_ADMIN_DYADS_ID_CUSTOM_CARDS_ID_IMAGE, { dyad_id: dyadId, card_id: props.id }) : undefined, [dyadId, props.id]),
        cardInfo?.image_filename
    )

    const onRemoveClick=useCallback(()=>{
        if(dyadId != null && window.confirm("Remove this card?")) {
            dispatch(removeUserDefinedCard(dyadId, props.id))
        }
    }, [dyadId, props.id])

    return <Card size="small" cover={<Image rootClassName="aspect-square w-full" src={imageSource || undefined}/>} actions={[
        <Button type="text" onClick={onRemoveClick} className="w-full"><TrashIcon className="w-4 h-4 text-red-400"/></Button>
    ]}>
        <Card.Meta title={cardInfo?.label_localized} description={cardInfo?.category}/>
    </Card>
}

export const CustomCardsPage = () => {

    const dispatch = useDispatch()

    const dyadId = useDyadId()

    const cardIds = useSelector(userDefinedCardSelectors.selectIds)

    console.log(cardIds)

    const [cardIdToEdit, setCardIdToEdit] = useState<string|undefined>(undefined)
    const [isModalOpen, setIsModalOpen] = useState(false)

    const onEditClick = useCallback((id: string) => {
        setCardIdToEdit(id)
        setIsModalOpen(true)
    }, [])

    const onAddNewClick = useCallback(()=>{
        setCardIdToEdit(undefined)
        setIsModalOpen(true)
    }, [])

    const onModalCloseRequested = useCallback(()=>{
        setIsModalOpen(false)
    }, [])

    useEffect(()=>{
        if(dyadId != null){
            dispatch(fetchUserDefinedCards(dyadId))
        }
    }, [dyadId])

    return <div>
        {cardIds.length == 0 ? <div className="p-10">No custom cards defined.</div> : <div className="grid grid-cols-4 gap-4 m-10">
            {
                cardIds.map(id => <CustomCardElement id={id} key={id}/>)
            }
            </div>}
        <Button className="ml-10" onClick={onAddNewClick}>Add Custom Card</Button>
        {
            dyadId != null ? <CustomCardModal open={isModalOpen} dyadId={dyadId} cardId={cardIdToEdit} onClose={onModalCloseRequested} onCancel={onModalCloseRequested}/> : null
        }
        
    </div>
}