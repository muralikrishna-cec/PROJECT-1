import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {  NavbarComponent } from './components/navbar/navbar';
import { Footer } from './components/footer/footer';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent, Footer],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class App {
  protected readonly title = signal('ai-code-review-frontend');
}
