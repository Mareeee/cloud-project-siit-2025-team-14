import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Subscription } from '../models/subscription.model';
import { environment } from '../../env/environment';
import { CreateSubscription } from '../models/create-subscription.model';


@Injectable({
  providedIn: 'root'
})
export class SubscriptionsService {

  private stagePath = '/dev';
  private resourcePath = '/subscriptions';
  private url = environment.apiBaseUrl + this.stagePath + this.resourcePath;

  constructor(private http: HttpClient) {}

  getSubscriptions(userId: string): Observable<{ data: Subscription[] }> {
    const params = new HttpParams().set('userId', userId);
    return this.http.get<{ data: Subscription[] }>(this.url, { params });
  }

  deleteSubscription(subscriptionId: string): Observable<any> {
    const params = new HttpParams().set('subscriptionId', subscriptionId.toString());
    return this.http.delete(this.url, { params });
  }

  createSubscription(subscription: CreateSubscription): Observable<any> {
    return this.http.post(this.url, subscription);
  }
}
