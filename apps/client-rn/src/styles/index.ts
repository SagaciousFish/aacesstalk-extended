import { TopicCategory } from "@aacesstalk/libs/ts-core";
import { StyleSheet } from "react-native";
const colors = require('./colors')

export const fontFamilyByWeight = {
    light: "NanumSquareNeo-Light",
    regular: "NanumSquareNeo-Regular",
    semibold: "NanumSquareNeo-Bold",
    bold: "NanumSquareNeo-Extrabold",
    extrabold: "NanumSquareNeo-Heavy",
  };

export const styleTemplates = StyleSheet.create({
    withLightFont: {"fontFamily": fontFamilyByWeight.light},
    withRegularFont: {"fontFamily": fontFamilyByWeight.regular},
    withSemiboldFont: {"fontFamily": fontFamilyByWeight.semibold},
    withBoldFont: {"fontFamily": fontFamilyByWeight.bold},
    withExtraboldFont: {"fontFamily": fontFamilyByWeight.extrabold},
    withHandwritingFont: {"fontFamily": "KyoboHandwriting2019"}
})

export function getTopicColorClassNames(topicCategory: TopicCategory): [string, string]{
  switch(topicCategory){
    case TopicCategory.Plan:
        return ["bg-topicplan-fg", "bg-topicplan-dimmed"]
    case TopicCategory.Recall:
        return ["bg-topicrecall-fg", "bg-topicrecall-dimmed"]
    case TopicCategory.Free:
        return ["bg-topicfree-fg", "bg-topicfree-dimmed"]
  }
}

export function getTopicColors(topicCategory: TopicCategory): {
  fg: string,
  bg: string,
  ribbon: string,
  dimmed: string
} {
  return colors[`topic${topicCategory}`]
}

export namespace TailwindClasses{
  export const ICON_BUTTON_SIZES="w-16 h-16"
}