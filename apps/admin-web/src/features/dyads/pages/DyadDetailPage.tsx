import { Button, Layout, Menu, MenuProps } from "antd"
import { Link, Outlet, useLocation, useMatch, useNavigate, useRoutes } from "react-router-dom"
import { ChatBubbleLeftRightIcon, PhotoIcon, HeartIcon } from '@heroicons/react/16/solid'
import { useCallback, useEffect } from "react";
import { useDispatch, useSelector } from "../../../redux/hooks";
import { dyadsSelectors, loadOneDyad } from "@aacesstalk/libs/ts-core";


type MenuItem = Required<MenuProps>['items'][number];

const NavItems: Array<MenuItem> = [{
    key: "sessions",
    icon: <ChatBubbleLeftRightIcon className="w-4 h-4"/>,
    label: "Dialogue Sessions"
}, {
    key: "custom-cards",
    icon: <PhotoIcon className="w-4 h-4"/>,
    label: "Custom Cards"
}, {
    key: "free-topics",
    icon: <HeartIcon className="w-4 h-4"/>,
    label: "Free Topics"
}]

export const DyadDetailPage = () =>{ 


    const dispatch = useDispatch()

    const nav = useNavigate()

    const urlMatch = useMatch('/dyads/:userId/:route')

    const onNavClick = useCallback((args: {key: string})=>{
        if(urlMatch?.params.route != args.key){
            nav(args.key)
        }
    }, [nav, urlMatch?.params.route])


    const dyad = useSelector(state => dyadsSelectors.selectById(state, urlMatch?.params.userId || ""))

    useEffect(()=>{
        const userId = urlMatch?.params.userId
        if(userId != null){
            dispatch(loadOneDyad(userId))
        }
    }, [urlMatch?.params.userId])

    return <Layout className="h-[100vh]">
        <Layout.Header className="p-6 bg-white border-b-2 border-slate-300 flex flex-row items-center">
            <Link to="/dyads"><Button size="small">Back to List</Button></Link>
            <div className="text-lg ml-5"><span className="font-bold mr-6">Dyad Info</span> {dyad != null ? <span className="capitalize">{dyad?.alias} ({dyad?.child_name} / {dyad?.child_gender} / {dyad?.parent_type})</span> : null}</div>
        </Layout.Header>
        <Layout className="bg-white h-full">
        <Layout.Sider className="!bg-white">
          <Menu className="h-full" items={NavItems} 
            selectedKeys={urlMatch != null ? [urlMatch.params.route!]: undefined}
            onClick={onNavClick}
            />
        </Layout.Sider>
        <Layout.Content>
            <Outlet/>
        </Layout.Content>
        </Layout>
        
        </Layout>
}