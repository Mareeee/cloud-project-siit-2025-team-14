import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';
import { Amplify } from 'aws-amplify';

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: 'eu-central-1_rECVsrzxp',
      userPoolClientId: '5eg4n6jko1b89s2q1t91h4o7f6',
      region: 'eu-central-1',
      loginWith: {
        username: true,
        email: false
      }
    } as any
  }
}, { ssr: false });

platformBrowserDynamic()
  .bootstrapModule(AppModule, { ngZoneEventCoalescing: true })
  .catch(err => console.error(err));
