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