import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, Router } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  async canActivate(route: ActivatedRouteSnapshot): Promise<boolean> {
    const isAuth = await this.authService.isAuthenticated();
    if (!isAuth) {
      this.router.navigate(['/login']);
      return false;
    }

    const expectedRole = route.data['role'] as string | undefined;
    if (expectedRole) {
      const userRole = await this.authService.getUserRole();
      if (userRole !== expectedRole) {
        this.router.navigate(['/']);
        return false;
      }
    }

    return true;
  }
}
