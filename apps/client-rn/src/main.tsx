import { AppRegistry } from 'react-native';
import App from './app/App';
import './i18n';
import './utils/net-info'

console.log("Registry")

AppRegistry.registerComponent('ClientRn', () => App);
