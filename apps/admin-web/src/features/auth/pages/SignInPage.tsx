import {Button, Input, Card, Form} from 'antd'
import { useCallback, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { FormItem } from 'react-hook-form-antd'
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup'
import { loginAdminThunk } from '@aacesstalk/libs/ts-core';
import { useDispatch, useSelector } from '../../../redux/hooks';
import { useNavigate } from 'react-router-dom';

const loginSchema = yup.object().shape({
    password: yup.string().min(6).required()
})

export const SignInPage = () => {

    const nav = useNavigate()

    const dispatch = useDispatch()

    const { control, handleSubmit, setError } = useForm({
        resolver: yupResolver(loginSchema)
    })

    const authError = useSelector(state => state.auth.error)

    useEffect(()=>{
        if(authError != null){
            setError("password", {message: "Sign in failed. Check password."})
        }
    }, [authError])

    const submit = useCallback(({ password }: {password: string})=>{
        dispatch(loginAdminThunk(password, () => {
            nav('/dyads')
        }))
    }, [])

    return <div className='container mx-auto px-10 py-10 flex flex-col'>
            <Card className='self-center'>
                <div className="text-lg font-bold">Sign In with Admin Password</div>
                <Form onFinish={handleSubmit(submit)}>
                    <FormItem control={control} name="password">
                        <Input.Password placeholder='Admin password' className="mt-4"/>
                    </FormItem>
                    <Button type="default" htmlType='submit' className='mt-2'>Submit</Button>
                </Form>
            </Card>
        </div>
}