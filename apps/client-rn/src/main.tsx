import { AppRegistry } from 'react-native';
import App from './app/App';
import './i18n';

console.log("Registry")

AppRegistry.registerComponent('ClientRn', () => App);
