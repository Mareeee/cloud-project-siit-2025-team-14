import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { signUp } from 'aws-amplify/auth';

@Component({
  selector: 'app-registration',
  templateUrl: './registration.component.html',
  styleUrls: ['./registration.component.css'],
})
export class RegistrationComponent {
  registerForm: FormGroup;
  submitted = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private fb: FormBuilder,
    private snackBar: MatSnackBar,
    private router: Router
  ) {
    this.registerForm = this.fb.group({
      firstName: ['', [Validators.required]],
      lastName: ['', [Validators.required]],
      birthdate: ['', [Validators.required]],
      username: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      password: [
        '',
        [
          Validators.required,
          Validators.minLength(8),
          Validators.pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/),
        ],
      ],
    });
  }

  get f() {
    return this.registerForm.controls;
  }

  async onSubmit() {
    this.submitted = true;
    this.errorMessage = '';
    this.successMessage = '';

    if (this.registerForm.invalid) return;

    const { firstName, lastName, birthdate, username, email, password } =
      this.registerForm.value;

    try {
      const result = await signUp({
        username,
        password,
        options: {
          userAttributes: {
            given_name: firstName,
            family_name: lastName,
            birthdate: birthdate,
            email: email,
          },
        },
      });

      this.snackBar.open(
        'Successful registration. You can now log in.',
        'Close',
        {
          duration: 3000,
        }
      );

      this.router.navigate(['/login']);
    } catch (error: any) {
      console.error('Signup error:', error);
      this.errorMessage = error.message || 'Error occurred.';
      this.snackBar.open(this.errorMessage, 'Close', {
        duration: 3000,
      });
    }
  }
}
