import { Routes } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard';
import { DrugsComponent } from './drugs/drugs';

export const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'drugs', component: DrugsComponent },
  // Add more routes here
];
