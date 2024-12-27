import { CardCategory, createUserDefinedCard } from "@aacesstalk/libs/ts-core"
import { yupResolver } from "@hookform/resolvers/yup"
import { Button, Form, Input, Modal, ModalProps, Select, Upload, Radio } from "antd"
import { useCallback } from "react"
import { useForm } from "react-hook-form"
import { FormItem } from "react-hook-form-antd"
import * as yup from 'yup'
import { useDispatch } from "../../../redux/hooks"

const CARD_CATEGORIES = [CardCategory.Core, CardCategory.Topic, CardCategory.Action, CardCategory.Emotion]

const CARD_CATEGORIES_OPTIONS = CARD_CATEGORIES.map(c => ({label: c.toUpperCase(), value: c}))

const schema = yup.object().shape({
    label: yup.string().min(1).trim().optional(),
    label_localized: yup.string().min(1).trim().required(),
    category: yup.string().oneOf(CARD_CATEGORIES).required(),
    image: yup.mixed().required() 
})

export const CustomCardModal = (props: Pick<ModalProps, "open"|"onCancel"|"onClose"> & {
    cardId?: string | undefined,
    dyadId: string
}) => {
    const dispatch = useDispatch()

    const {control, handleSubmit, reset} = useForm({
        resolver: yupResolver(schema)
    })

    const getFileObjFromImageEvent = useCallback((args: any)=>{
        return args.file.originFileObj
    }, [])

    const onClose = useCallback((ev: any)=>{
        reset()
        props.onClose?.(ev)
    }, [props.onClose])

    const onCancel = useCallback((ev:any)=>{
        reset()
        props.onCancel?.(ev)
    }, [props.onCancel])

    const submit = useCallback(async (values: any) => {

        if(props.cardId != null){
            //Edit mode
            const formData = new FormData()
            /*
            if(values.subtopic != detailToModify.subtopic){
                formData.append("topic", values.subtopic)
            }

            if(values.subtopic_description != detailToModify.subtopic_description){
                formData.append("description", values.subtopic_description)
            }

            formData.append("remove_image", values.remove_image)
            if(values.image != null){
                formData.append("image", values.image.file.originFileObj)
            }

            dispatch(updateFreeTopicDetail(props.dyadId, props.topicId, formData, () => {
                clearAndClose()
            }))*/

        }else{
            //Creation mode
            const formData = new FormData()
            formData.append("label", values.label)
            formData.append("label_localized", values.label_localized)
            formData.append("category", values.category)
            formData.append("image", values.image.file.originFileObj)
            
            dispatch(createUserDefinedCard(props.dyadId, formData, () => {
                onClose({})
            }))
        }

    }, [props.dyadId, props.cardId, onClose])

    return <Modal title={props.cardId != null ? "Edit Custom Card" : "Add New Custom Card"} 
            open={props.open} onClose={onClose} onCancel={onCancel} maskClosable={false} 
            okText={props.cardId != null ? "Update" : "Create"} okButtonProps={{htmlType: 'submit', "form": "custom-card-form"}}
            destroyOnClose={true}>
        <Form onFinish={handleSubmit(submit)} id="custom-card-form">
                
            <FormItem control={control} name="label_localized">
                <Input placeholder="Card label in Korean"/>
            </FormItem>

            <FormItem control={control} name="category">
                <Radio.Group options={CARD_CATEGORIES_OPTIONS} optionType="button" buttonStyle="solid"/>
            </FormItem>

            <FormItem control={control} name="label">
                <Input placeholder="Label in English (Optional)"/>
            </FormItem>

            <FormItem control={control} name="image" getValueFromEvent={getFileObjFromImageEvent}>
                <Upload listType="picture" maxCount={1} multiple={false} accept={"image/png, image/jpeg"}>
                    <Button type="dashed">Upload Image</Button>
                </Upload>
            </FormItem>
        </Form>
    </Modal>
}