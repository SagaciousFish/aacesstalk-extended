import { FreeTopicDetail } from "@aacesstalk/libs/ts-core";
import { yupResolver } from "@hookform/resolvers/yup";
import { Button, Form, Input, Modal, ModalProps, Upload } from "antd";
import { useCallback, useState } from "react";
import { useForm } from "react-hook-form";
import { FormItem } from "react-hook-form-antd";
import * as yup from 'yup'

const schema = yup.object().shape({
    subtopic: yup.string().min(1).trim().required(),
    subtopic_description: yup.string().min(1).trim().required(),
    image: yup.mixed().optional() 
})

export const FreeTopicModal = (props: Pick<ModalProps, "open"|"onCancel"|"onClose"> & {
    topicId?: string | undefined
}) => {

    const {control, handleSubmit} = useForm({
        resolver: yupResolver(schema)
    })

    const [imageFile, setImageFile] = useState(null)

    const submit = useCallback((values: any) => {
        console.log(values, imageFile)
    }, [imageFile])

    const onFileChange = useCallback((args: any)=>{
        setImageFile(args.file)
    }, [])

    return <Modal title={props.topicId != null ? "Edit Topic" : "New Free Topic"} 
        open={props.open} onCancel={props.onCancel} maskClosable={false} okButtonProps={{htmlType: "submit", form: "free-topic-form"}}>
        <Form onFinish={handleSubmit(submit)} id="free-topic-form">
            <FormItem control={control} name="subtopic">
                <Input placeholder="Topic (Korean)"/>
            </FormItem>       

            <FormItem control={control} name="subtopic_description">
                <Input.TextArea placeholder="Topic description (English)"/>
            </FormItem>

            <Upload listType="picture" onChange={onFileChange} maxCount={1} multiple={false} accept={"image/png, image/jpeg"}>
                <Button type="dashed">Upload Image</Button>
            </Upload>
        </Form>
    </Modal>
}