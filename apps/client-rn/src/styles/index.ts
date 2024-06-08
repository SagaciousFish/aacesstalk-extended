import { TopicCategory } from "@aacesstalk/libs/ts-core";
import { StyleSheet } from "react-native";

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

export function getTopicColors(topicCategory: TopicCategory): [string, string]{
  switch(topicCategory){
    case TopicCategory.Plan:
        return ["bg-topicplan-fg", "bg-topicplan-dimmed"]
    case TopicCategory.Recall:
        return ["bg-topicrecall-fg", "bg-topicrecall-dimmed"]
    case TopicCategory.Free:
        return ["bg-topicfree-fg", "bg-topicfree-dimmed"]
  }
}