import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type AppRole = 'guest' | 'user' | 'admin';

@Injectable({ providedIn: 'root' })
export class AuthRoleService {
    private _role$ = new BehaviorSubject<AppRole>('guest');
    role$ = this._role$.asObservable();

    setRole(role: AppRole) { this._role$.next(role); }
}
