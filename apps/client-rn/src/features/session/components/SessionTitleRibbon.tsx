import {Text, View} from 'react-native'
import { SessionTopicInfo, TopicCategory } from "@aacesstalk/libs/ts-core"
import { useSelector } from "apps/client-rn/src/redux/hooks"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import format from "string-template"
import { styleTemplates } from 'apps/client-rn/src/styles'
import Svg, {
    Path,
    Mask,
    G,
    Defs,
    LinearGradient,
    Stop
  } from "react-native-svg"

import * as colors from '../../../styles/colors'

function RibbonEnd(props:{svgClassName?:string, fgColor?: string, direction: "left"|"right"}) {
  return (
    <Svg
      className={`w-[70] h-20 ${props.svgClassName}`}
      viewBox="0 0 78 58"
      fill="none"
    >
      {props.direction == "left" ? <><Path
        d="M10.64 17.559C6.455 9.574 12.246 0 21.26 0h44.184c6.623 0 11.992 5.369 11.992 11.992v34.016c0 6.623-5.37 11.992-11.992 11.992H21.261c-9.015 0-14.806-9.574-10.621-17.559L16.637 29 10.64 17.559z"
        fill={props.fgColor || "#78AAFC"}
      />
      <Mask
        id="a"
        maskUnits="userSpaceOnUse"
        x={8}
        y={0}
        width={70}
        height={58}
      >
        <Path
          d="M10.26 17.584C6.05 9.6 11.84 0 20.869 0h44.577c6.623 0 11.992 5.369 11.992 11.992v34.016C77.437 52.631 72.068 58 65.445 58H20.868c-9.027 0-14.818-9.599-10.607-17.584l3.07-5.823a11.992 11.992 0 000-11.186l-3.07-5.823z"
          fill="url(#paint0_linear_130_1665)"
        />
      </Mask>
      <G mask="url(#a)">
        <Path
          d="M77.437 32.98h-29.98l14.99 12.51L77.437 58V32.98z"
          fill="#000"
          fillOpacity={0.4}
        />
      </G></> : <>
      <Path
        d="M67.36 17.559C71.545 9.574 65.754 0 56.739 0H12.555C5.932 0 .563 5.369.563 11.992v34.016C.563 52.631 5.932 58 12.555 58h44.184c9.015 0 14.806-9.574 10.62-17.559L61.364 29l5.997-11.441z"
        fill={props.fgColor || "#78AAFC"}
      />
      <Mask
        id="a"
        maskUnits="userSpaceOnUse"
        x={0}
        y={0}
        width={70}
        height={58}
      >
        <Path
          d="M67.74 17.584C71.95 9.6 66.16 0 57.132 0H12.555C5.932 0 .563 5.369.563 11.992v34.016C.563 52.631 5.932 58 12.555 58h44.577c9.027 0 14.818-9.599 10.608-17.584l-3.07-5.823a11.992 11.992 0 010-11.186l3.07-5.823z"
          fill="url(#paint0_linear_130_1665)"
        />
      </Mask>
      <G mask="url(#a)">
        <Path
          d="M.563 32.98h29.98l-14.99 12.51L.563 58V32.98z"
          fill="#000"
          fillOpacity={0.4}
        />
      </G></>}
      <Defs>
        <LinearGradient
          id="paint0_linear_130_1665"
          x1={39.2132}
          y1={0}
          x2={39.2132}
          y2={58.0001}
          gradientUnits="userSpaceOnUse"
        >
          <Stop stopColor="#F05" />
          <Stop offset={1} stopColor="#C70042" />
        </LinearGradient>
      </Defs>
    </Svg>
  )
}


export const SessionTitleRibbon = (props: {
    topic: SessionTopicInfo,
    titleClassName?: string,
    containerClassName?: string
}) => {

    const {t} = useTranslation()

    const child_name = useSelector(state => state.auth.dyadInfo?.child_name)
    
    const label = useMemo(()=>{
        switch(props.topic.category){
            case TopicCategory.Plan:
                return t("TopicSelection.Plan")
            case TopicCategory.Recall:
                return t("TopicSelection.Recall")
            case TopicCategory.Free:
                return format(t("TopicSelection.FreeTemplate"), {child_name})
        }
    }, [t, child_name, props.topic.category])

    return <View className={`${props.containerClassName}`}>
        <View id='ribbon-body' className={`rounded-lg h-14 justify-center px-7 shadow-lg shadow-slate-700 bg-topic${props.topic.category.toLowerCase()}-fg`}>
            <Text style={styleTemplates.withBoldFont} className={`text-white text-lg ${props.titleClassName}`}>{label}</Text>
        </View>
        <RibbonEnd direction='left' svgClassName='absolute z-[-1] left-[-40px]' fgColor={colors[`topic${props.topic.category}`].ribbon}/>
        <RibbonEnd direction='right' svgClassName='absolute z-[-1] right-[-40px]' fgColor={colors[`topic${props.topic.category}`].ribbon}/>
    </View>
}