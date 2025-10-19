import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';
import { Amplify } from 'aws-amplify';

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: 'eu-central-1_QQehr70CL',
      userPoolClientId: '20i01obp5o19hpierc7ijqrvf4',
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
