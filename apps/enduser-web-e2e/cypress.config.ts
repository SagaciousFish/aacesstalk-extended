import { nxE2EPreset } from '@nx/cypress/plugins/cypress-preset';

import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    ...nxE2EPreset(__filename, {
      cypressDir: 'src',
      bundler: 'vite',
      webServerCommands: {
        default: 'nx run aacesstalk-web-user:serve',
        production: 'nx run aacesstalk-web-user:preview',
      },
      ciWebServerCommand: 'nx run aacesstalk-web-user:serve-static',
    }),
    baseUrl: 'http://localhost:4200',
  },
});
