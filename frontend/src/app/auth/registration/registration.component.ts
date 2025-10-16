import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-registration',
  templateUrl: './registration.component.html',
  styleUrl: './registration.component.css'
})
export class RegistrationComponent {
  registerForm: FormGroup;
  submitted = false;

  constructor(private fb: FormBuilder) {
    this.registerForm = this.fb.group({
      firstName: ['', [Validators.required]],
      lastName: ['', [Validators.required]],
      birthdate: ['', [Validators.required]],
      username: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [
        Validators.required,
        Validators.minLength(8),
        Validators.pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/)
      ]]
    });
  }

  get f() {
    return this.registerForm.controls;
  }

  onSubmit() {
    this.submitted = true;
    if (this.registerForm.invalid) {
      return;
    }

    const data = this.registerForm.value;
    console.log('Registracija podaci:', data);
  }
}
