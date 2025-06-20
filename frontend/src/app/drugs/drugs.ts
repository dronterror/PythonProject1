import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-drugs',
  imports: [],
  templateUrl: './drugs.html',
  styleUrl: './drugs.css'
})
export class DrugsComponent implements OnInit {
  drugs: any[] = [];

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getDrugs().subscribe(data => {
      this.drugs = data;
    });
  }
}
