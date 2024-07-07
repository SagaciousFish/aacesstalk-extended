import { ChildGender, ParentType, createDyad } from '@aacesstalk/libs/ts-core'
import { yupResolver } from '@hookform/resolvers/yup'
import { Modal, Form, Input, Select, ButtonProps } from 'antd'
import { useDispatch, useSelector } from '../../../redux/hooks'
import { useCallback, useEffect, useMemo } from 'react'
import { useForm } from 'react-hook-form'
import { FormItem } from 'react-hook-form-antd'
import * as yup from 'yup'

const CHILD_GENDERS = [ChildGender.Girl, ChildGender.Boy]
const CHILD_GENDERS_OPTIONS = CHILD_GENDERS.map(g => ({value: g, label: <span className='capitalize'>{g}</span>}))
const PARENT_TYPES = [ParentType.Mother, ParentType.Father]
const PARENT_TYPES_OPTIONS = PARENT_TYPES.map(g => ({value: g, label: <span className='capitalize'>{g}</span>}))

const creationSchema = yup.object().shape({
    alias: yup.string().required().trim().min(1).matches(/[a-zA-Z0-9\-_]+/, {message: "Alias should consist of alphanumeric letters, hyphens, and underscores."}),
    child_name: yup.string().required().trim().min(1),
    child_gender: yup.string().required().oneOf(CHILD_GENDERS),
    parent_type: yup.string().required().oneOf(PARENT_TYPES)
})

export const CreateDyadModal = (props: {
    open: boolean,
    onClose: () => void
}) => {

    const dispatch = useDispatch()

    const {control, handleSubmit, reset, setError, formState: {errors}} = useForm({resolver: yupResolver(creationSchema), defaultValues: {child_gender: ChildGender.Boy, parent_type: ParentType.Father}})
    
    const clearAndClose = useCallback(()=>{
        reset()
        props.onClose()
    }, [props.onClose])

    const submitDyadInfo = useCallback((values: any) => {
        dispatch(createDyad(values, (dyad) => {
            clearAndClose()
        }, (err) => {
            setError('root', {message: "Dyad creation failed."})
        }))
    }, [clearAndClose])


    useEffect(()=>{
        return () =>{

        }
    }, [])

    const isCreating = useSelector(state => state.dyads.isCreatingDyad)

    const okButtonProps: ButtonProps = useMemo(()=>{
        return {"htmlType": "submit", form: "new-dyad-form", disabled: isCreating}
    }, [isCreating])

    const cancelButtonProps: ButtonProps | undefined = useMemo(() => {
        return isCreating === true ? {hidden: true} : undefined
    }, [isCreating])
    
    
    return <Modal okButtonProps={okButtonProps} cancelButtonProps={cancelButtonProps} okText={isCreating === true ? "Creating..." : "Create"} maskClosable={false}
            title="Create Dyad" open={props.open} onCancel={clearAndClose} destroyOnClose={true} onClose={clearAndClose}>
        <Form labelCol={{span: 5}} preserve={false} onFinish={handleSubmit(submitDyadInfo)} id="new-dyad-form">
            <FormItem control={control} name="alias" label="Alias">
                <Input placeholder="Dyad's alias (Only shown to researcher)"/>
            </FormItem>

            <FormItem control={control} name="child_name" label="Child Name">
                <Input placeholder="Child' name (마지막 글자에 받침이 있을 시 '이'를 붙이세요)"/>
            </FormItem>

            <FormItem control={control} name="child_gender" label="Child Gender">
                <Select options={CHILD_GENDERS_OPTIONS} defaultValue={CHILD_GENDERS_OPTIONS[0]}/>
            </FormItem>


            <FormItem control={control} name="parent_type" label="Parent Type">
                <Select options={PARENT_TYPES_OPTIONS} defaultValue={PARENT_TYPES_OPTIONS[0]}/>
            </FormItem>

            {
                errors.root != null ? <div className='text-red-400'>{errors.root.message}</div> : null
            }
        </Form>
    </Modal>
}