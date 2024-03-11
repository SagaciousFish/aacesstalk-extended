// eslint-disable-next-line @typescript-eslint/no-unused-vars
import styles from './app.module.css';

import NxWelcome from './nx-welcome';
import { tsCore } from '@aacesstalk/libs/ts-core';

export function App() {
  return (
    <div>
      <NxWelcome title="aacesstalk-web-user" />
      <div>{tsCore()}</div>
    </div>
  );
}

export default App;
