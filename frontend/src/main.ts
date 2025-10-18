import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';
import { Amplify } from 'aws-amplify';

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: 'eu-central-1_HvYMuf4qA',
      userPoolClientId: '75pboe7ffcd0irquh8hh5psgd0',
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
