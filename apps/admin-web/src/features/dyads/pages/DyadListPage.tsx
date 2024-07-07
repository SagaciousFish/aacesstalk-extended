import { useDispatch, useSelector } from "../../../redux/hooks"
import { useCallback, useEffect, useState } from "react"
import { DyadWithPasscode, dyadsSelectors, loadDyads } from '@aacesstalk/libs/ts-core'
import { Button, Card, Space, Table } from "antd"
import { ColumnsType } from "antd/es/table"
import { Link } from "react-router-dom"
import { CreateDyadModal } from "../components/CreateDyadModal"

const columns: ColumnsType<DyadWithPasscode> = [{
    title: "Alias",
    dataIndex: "alias",
    key: 'name'
}, {
    title: "Child Name",
    dataIndex: 'child_name',
    key:'child_name'
}, {
    title: "Child Gender",
    dataIndex: "child_gender",
    key:'child_gender'
}, {
    title: 'Parent Type',
    dataIndex: 'parent_type',
    key:'parent_type'
}, {
    title: 'Passcode',
    dataIndex: 'passcode',
    key: 'passcode'
},{
    title: "Actions",
    key: "action",
    render: (_, dyad) => {
        return <Space key="action" size="middle">
            <Link to={`/dyads/${dyad.id}`}>
                <Button>Detail</Button>
            </Link>
        </Space>
    }
}]

export const DyadListPage = () => {

    const dispatch = useDispatch()

    const dyads = useSelector(dyadsSelectors.selectAll)

    const [isCreationModalOpen, setIsCreationModalOpen] = useState<boolean>(false)

    const onCreateDyadClick = useCallback(()=>{
        setIsCreationModalOpen(true)
    }, [])


    const closeCreateDyadModal = useCallback(()=>{
        setIsCreationModalOpen(false)
    }, [])

    useEffect(()=>{
        dispatch(loadDyads())
    }, [])

    return <div className='container mx-auto px-10 py-10 flex flex-col'>
        <div className="text-lg font-bold mb-3 ml-1">Dyads</div>
        <Table dataSource={dyads} columns={columns}/>
        <Button className="self-start" onClick={onCreateDyadClick}>Create Dyad</Button>
        <CreateDyadModal open={isCreationModalOpen} onClose={closeCreateDyadModal}/>
    </div>
}