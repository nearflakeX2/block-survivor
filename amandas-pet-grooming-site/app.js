const services = [
  { name: 'Bath + Brush', time: '60–90 min', price: 45, desc: 'Coat wash, blow dry, brush out, ear cleaning, and finishing spray.' },
  { name: 'Full Groom', time: '90–150 min', price: 78, desc: 'Bath + brush with haircut, trimming, sanitary trim, and nail clipping.' },
  { name: 'Puppy Intro Groom', time: '45–60 min', price: 38, desc: 'Gentle first-time grooming session to build comfort and confidence.' },
  { name: 'Nail Trim + Paw Care', time: '15–25 min', price: 18, desc: 'Quick nail trim, paw tidy, and moisturizing paw balm.' },
  { name: 'Deshedding Treatment', time: '60–120 min', price: 62, desc: 'Specialized treatment to reduce shedding and maintain coat health.' },
  { name: 'Cat Grooming', time: '45–90 min', price: 55, desc: 'Cat-safe handling with brushing, mat removal, and hygiene trim.' }
];

const reviews = [
  '“Can\'t say enough about the service and staff at Amanda\'s!”',
  '“Hands down the best groomer in town.”',
  '“Super fast and my kitty didn\'t fuss at getting her nails clipped!”'
];

const serviceGrid = document.getElementById('serviceGrid');
const reviewGrid = document.getElementById('reviewGrid');
const serviceSelect = document.getElementById('serviceSelect');

serviceGrid.innerHTML = services.map(s => `
  <article class="card">
    <h3>${s.name}</h3>
    <p>${s.desc}</p>
    <p><strong>${s.time}</strong></p>
    <p class="price">Starting at $${s.price}</p>
  </article>
`).join('');

reviewGrid.innerHTML = reviews.map(r => `<article class="review">${r}</article>`).join('');

serviceSelect.innerHTML = services.map(s => `<option>${s.name}</option>`).join('');

document.getElementById('bookingForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const data = new FormData(e.target);
  document.getElementById('formMessage').textContent = `Thanks ${data.get('owner')} — your request for ${data.get('pet')} has been saved. We'll call ${data.get('phone')} to confirm.`;
  e.target.reset();
});

document.getElementById('year').textContent = new Date().getFullYear();
