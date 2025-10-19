import { Injectable } from '@angular/core';
import { Hub } from 'aws-amplify/utils';
import { signOut, getCurrentUser, fetchAuthSession } from 'aws-amplify/auth';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private user: any = null;
  private token: string | null = null;
  isLoggedIn$ = new BehaviorSubject<boolean>(false);
  userRole$ = new BehaviorSubject<string | null>(null);

  constructor() {
    Hub.listen('auth', (data) => {
      const { payload } = data;
      if (payload.event === 'signedIn') {
        this.loadUser();
      }
      if (payload.event === 'signedOut') {
        this.clearSession();
      }
    });

    this.loadUser();
  }

  async loadUser() {
    try {
      const user = await getCurrentUser();
      const session = await fetchAuthSession();
      const idToken = session.tokens?.idToken?.toString();

      this.user = user;
      this.token = idToken || null;

      if (this.token) {
        localStorage.setItem('token', this.token);
      }

      const role = await this.getUserRole();
      this.isLoggedIn$.next(true);
      this.userRole$.next(role);

    } catch {
      this.clearSession();
    }
  }

  async getUser() {
    if (!this.user) await this.loadUser();
    return this.user;
  }

  async getToken() {
    if (!this.token) await this.loadUser();
    return this.token;
  }

  async getUserRole(): Promise<string | null> {
    try {
      const session = await fetchAuthSession();
      const idTokenPayload = session.tokens?.idToken?.payload ?? {};
      const groupsRaw = idTokenPayload['cognito:groups'];

      const groups = Array.isArray(groupsRaw) ? (groupsRaw as string[]) : [];

      return groups.length ? groups[0] : 'User';
    } catch {
      return null;
    }
  }

  async isAuthenticated(): Promise<boolean> {
    try {
      const user = await getCurrentUser();
      return !!user;
    } catch {
      return false;
    }
  }

  async logout() {
    await signOut();
    this.clearSession();
  }

  private clearSession() {
    this.user = null;
    this.token = null;
    localStorage.removeItem('token');
    this.isLoggedIn$.next(false);
    this.userRole$.next(null);
  }
}
