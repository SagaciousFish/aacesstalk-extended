import { adminFreeTopicDetailsSelectors, createFreeTopicDetail, updateFreeTopicDetail } from "@aacesstalk/libs/ts-core";
import { yupResolver } from "@hookform/resolvers/yup";
import { Button, Form, Input, Modal, ModalProps, Upload, Checkbox } from "antd";
import { useDispatch, useSelector } from "../../../redux/hooks";
import { useCallback, useEffect } from "react";
import { useForm } from "react-hook-form";
import { FormItem } from "react-hook-form-antd";
import * as yup from 'yup'

const schema = yup.object().shape({
    subtopic: yup.string().min(1).trim().required(),
    subtopic_description: yup.string().min(1).trim().required(),
    remove_image: yup.boolean().optional(),
    image: yup.mixed().optional() 
})

export const FreeTopicModal = (props: Pick<ModalProps, "open"|"onCancel"|"onClose"> & {
    topicId?: string | undefined,
    dyadId: string
}) => {

    const dispatch = useDispatch()

    const detailToModify = useSelector(state => adminFreeTopicDetailsSelectors.selectById(state, props.topicId || ""))

    const {control, handleSubmit, reset} = useForm({
        resolver: yupResolver(schema)
    })

    const clearAndClose = useCallback(()=>{
        reset()
        props.onCancel?.({} as any)
    }, [props.onClose])

    const submit = useCallback(async (values: any) => {

        if(props.topicId != null){
            //Edit mode
            const formData = new FormData()
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
            }))

        }else{
            //Creation mode
            const formData = new FormData()
            formData.append("topic", values.subtopic)
            formData.append("description", values.subtopic_description)
            if(values.image != null){
                formData.append("image", values.image.file.originFileObj)
            }
            dispatch(createFreeTopicDetail(props.dyadId, formData, () => {
                clearAndClose()
            }))
        }


    }, [props.dyadId, props.topicId, detailToModify, clearAndClose])



    const getFileObjFromImageEvent = useCallback((args: any)=>{
        return args.file.originFileObj
    }, [])

    useEffect(()=>{
        if(props.topicId != null && detailToModify){
            reset({
                subtopic: detailToModify.subtopic,
                subtopic_description: detailToModify.subtopic_description,
                remove_image: false,
                image: undefined
            })
        }
    }, [props.topicId, detailToModify])


    return <Modal title={props.topicId != null ? "Edit Topic" : "New Free Topic"} 
        open={props.open} onCancel={props.onCancel} maskClosable={false} destroyOnClose={true} okButtonProps={{htmlType: "submit", form: "free-topic-form"}}>
        <Form onFinish={handleSubmit(submit)} id="free-topic-form">
            <FormItem control={control} name="subtopic">
                <Input placeholder="Topic (Korean)"/>
            </FormItem>       

            <FormItem control={control} name="subtopic_description">
                <Input.TextArea placeholder="Topic description (English)"/>
            </FormItem>

            {
                props.topicId != null ? <FormItem control={control} name="remove_image">
                    <Checkbox>Remove existing image</Checkbox>
                </FormItem> : null
            }
            <FormItem control={control} name="image" getValueFromEvent={getFileObjFromImageEvent}>
                <Upload listType="picture" maxCount={1} multiple={false} accept={"image/png, image/jpeg"}>
                    <Button type="dashed">Upload Image</Button>
                </Upload>
            </FormItem>
        </Form>
    </Modal>
}