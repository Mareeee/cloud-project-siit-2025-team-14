import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { signIn } from 'aws-amplify/auth';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { getCurrentUser } from 'aws-amplify/auth';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  submitted = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private snackBar: MatSnackBar,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required]],
      password: ['', [Validators.required]]
    });
  }

  async ngOnInit() {
    try {
      const user = await getCurrentUser();
      console.log('Trenutni korisnik:', user);
    } catch {
      console.log('Nema prijavljenog korisnika.');
    }
  }

  get f() {
    return this.loginForm.controls;
  }

  async onSubmit() {
    this.submitted = true;
    this.errorMessage = '';

    if (this.loginForm.invalid) return;

    const { username, password } = this.loginForm.value;

    try {
      await signIn({ username, password });
      this.router.navigate(['/dashboard']);
    } catch (error: any) {
      console.error('Login error:', error);
      this.errorMessage = error.message || 'Login failed.';
      this.snackBar.open(this.errorMessage, 'Close', { duration: 3000 });
    }
  }
}
