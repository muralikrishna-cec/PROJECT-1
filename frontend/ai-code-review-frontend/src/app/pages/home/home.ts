import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';


@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.html',
  imports: [RouterLink],
  styleUrls: ['./home.css'],
})
export class HomeComponent {

scrollTo(sectionId: string) {
  const section = document.getElementById(sectionId);
  if (section) {
    section.scrollIntoView({ behavior: 'smooth' });
  }
}

}