import { StyleSheet } from "react-native";
import { createTheme } from '@rneui/themed';
import nw from 'nativewind';

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
})

export const rneuiTheme = createTheme({
  components: {
    Button: {
      titleStyle: {
        ...styleTemplates.withBoldFont
      },
    }
  }
})