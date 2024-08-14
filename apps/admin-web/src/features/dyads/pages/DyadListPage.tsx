import { useDispatch, useSelector } from "../../../redux/hooks"
import { useCallback, useEffect, useState } from "react"
import { DyadWithPasscode, Http, dyadsSelectors, loadDyads } from '@aacesstalk/libs/ts-core'
import { Button, Card, Space, Table } from "antd"
import { ColumnsType } from "antd/es/table"
import { Link } from "react-router-dom"
import { CreateDyadModal } from "../components/CreateDyadModal"
import FileSaver from "file-saver"

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
    const token = useSelector(state => state.auth.jwt)

    const [isCreationModalOpen, setIsCreationModalOpen] = useState<boolean>(false)

    const onCreateDyadClick = useCallback(()=>{
        setIsCreationModalOpen(true)
    }, [])

    const onExportClick = useCallback(async ()=>{
        if(token != null){
            try{
                const resp = await Http.axios.get(Http.ENDPOINT_ADMIN_DATA_DIALOGUES, {
                    headers: await Http.getSignedInHeaders(token),
                    responseType: 'blob'
                })
                FileSaver.saveAs(resp.data)

            }catch(ex){
                console.log(ex)
            }
        }
    }, [token])

    const onDownloadDb = useCallback(async ()=>{
        if(token != null){
            try{
                const resp = await Http.axios.get(Http.ENDPOINT_ADMIN_DATA_DB_DOWNLOAD, {
                    headers: await Http.getSignedInHeaders(token),
                    responseType: 'blob'
                })
                FileSaver.saveAs(resp.data, "aacesstalk.sqlite3")

            }catch(ex){
                console.log(ex)
            }
        }
    }, [token])


    const onDownloadCards = useCallback(async ()=>{
        if(token != null){
            try{
                const resp = await Http.axios.get(Http.ENDPOINT_ADMIN_DATA_CARDS, {
                    headers: await Http.getSignedInHeaders(token),
                    responseType: 'blob'
                })
                const blob = new Blob([resp.data], { type: 'text/csv;charset=utf-8;' });

                FileSaver.saveAs(blob, "child_cards.csv")

            }catch(ex){
                console.log(ex)
            }
        }
    }, [token])



    const closeCreateDyadModal = useCallback(()=>{
        setIsCreationModalOpen(false)
    }, [])

    useEffect(()=>{
        dispatch(loadDyads())
    }, [])

    return <div className='container mx-auto px-10 py-10 flex flex-col'>
        <div className="text-lg font-bold mb-3 ml-1">Dyads</div>
        <div className="flex flex-wrap gap-2 mb-2">
            <Button onClick={onExportClick}>Export all sessions</Button>
            <Button onClick={onDownloadDb}>Download database</Button>

            <Button onClick={onDownloadCards}>Download card dataset</Button>
        </div>
        <Table dataSource={dyads} columns={columns}/>
        <Button className="self-start" onClick={onCreateDyadClick}>Create Dyad</Button>
        <CreateDyadModal open={isCreationModalOpen} onClose={closeCreateDyadModal}/>
    </div>
}