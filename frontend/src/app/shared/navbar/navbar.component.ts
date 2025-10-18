import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthRoleService, AppRole } from '../auth-role.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {
  role$: Observable<AppRole>;

  constructor(private auth: AuthRoleService) {
    this.role$ = this.auth.role$;
  }

  devSwitch(role: AppRole) {
    this.auth.setRole(role);
  }
}
