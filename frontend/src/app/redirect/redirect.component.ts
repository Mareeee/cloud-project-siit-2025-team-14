import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../auth/auth.service';

@Component({
  selector: 'app-redirect',
  template: ''
})
export class RedirectComponent implements OnInit {
  constructor(private router: Router, private authService: AuthService) {}

  async ngOnInit() {
    const isAuth = await this.authService.isAuthenticated();

    if (!isAuth) {
      this.router.navigate(['/login']);
      return;
    }

    const role = await this.authService.getUserRole();

    if (role === 'Admin') {
      this.router.navigate(['/admin/manage-content']);
    } else if (role === 'User') {
      this.router.navigate(['/feed']);
    } else {
      this.router.navigate(['/login']);
    }
  }
}
