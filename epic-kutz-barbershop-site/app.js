const services = [
  {name:'Signature Haircut',desc:'Consultation, precision cut, and clean finish.',price:35},
  {name:'Skin Fade + Lineup',desc:'Detailed fade with razor-sharp edge-up.',price:45},
  {name:'Haircut + Beard Combo',desc:'Cut, beard trim, and shaping.',price:55},
  {name:'Kids Cut (12 & under)',desc:'Clean, age-appropriate styles for younger clients.',price:28},
  {name:'Beard Sculpt + Hot Towel',desc:'Premium beard detail and hydration treatment.',price:30},
  {name:'VIP Groom Package',desc:'Full service cut, beard, enhancement, and styling.',price:70}
];

const grid = document.getElementById('servicesGrid');
const select = document.getElementById('serviceSelect');

grid.innerHTML = services.map(s => `
  <article class="card">
    <h3>${s.name}</h3>
    <p>${s.desc}</p>
    <p class="price">From $${s.price}</p>
  </article>
`).join('');

select.innerHTML = services.map(s => `<option>${s.name}</option>`).join('');

document.getElementById('bookingForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  document.getElementById('msg').textContent = `Thanks ${f.get('name')} — your ${f.get('service')} request was submitted. We'll call ${f.get('phone')} to confirm.`;
  e.target.reset();
});

document.getElementById('year').textContent = new Date().getFullYear();
