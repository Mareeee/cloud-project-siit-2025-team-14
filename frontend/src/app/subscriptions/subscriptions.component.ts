import { Component, OnInit } from '@angular/core';
import { SubscriptionsService } from '../services/subscriptions.service';
import { Subscription } from '../models/subscription.model';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../auth/auth.service';

@Component({
  selector: 'app-subscriptions',
  templateUrl: './subscriptions.component.html',
  styleUrls: ['./subscriptions.component.scss']
})
export class SubscriptionsComponent implements OnInit {
  subscriptions: Subscription[] = [];
  isLoading = true;
  errorMessage = '';

  constructor(
    private subscriptionsService: SubscriptionsService,
    private snackBar: MatSnackBar,
    private authService: AuthService
  ) {}

  async ngOnInit(): Promise<void> {
    try {
      this.isLoading = true;
      const userId = await this.authService.getUserId();

      if (!userId) {
        this.errorMessage = 'User not authenticated.';
        this.isLoading = false;
        return;
      }

      this.subscriptionsService.getSubscriptions(userId).subscribe({
        next: (response) => {
          this.subscriptions = response.data;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error loading subscriptions:', error);
          this.errorMessage = 'Failed to load subscriptions.';
          this.isLoading = false;
        }
      });
    } catch (error) {
      console.error('Error getting user ID:', error);
      this.errorMessage = 'Failed to get user information.';
      this.isLoading = false;
    }
  }

  unsubscribe(subscriptionId: string): void {
    this.subscriptionsService.deleteSubscription(subscriptionId).subscribe({
      next: () => {
        this.subscriptions = this.subscriptions.filter(sub => sub.subscriptionId !== subscriptionId);
        this.snackBar.open('Unsubscribed successfully.', 'Close', { duration: 3000 });
      },
      error: (error) => {
        console.error('Error deleting subscription:', error);
        this.errorMessage = 'Failed to unsubscribe.';
        this.snackBar.open('Failed to unsubscribe.', 'Close', { duration: 3000 });
      }
    });
  }
}
