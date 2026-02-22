const reviews = Array.from(document.querySelectorAll('.review'));
const dotsWrap = document.getElementById('dots');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
let idx = 0;

reviews.forEach((_, i) => {
  const d = document.createElement('button');
  d.className = 'dot' + (i === 0 ? ' active' : '');
  d.addEventListener('click', () => show(i));
  dotsWrap.appendChild(d);
});

function show(i) {
  idx = (i + reviews.length) % reviews.length;
  reviews.forEach((r, n) => r.classList.toggle('active', n === idx));
  Array.from(dotsWrap.children).forEach((d, n) => d.classList.toggle('active', n === idx));
}

prevBtn.addEventListener('click', () => show(idx - 1));
nextBtn.addEventListener('click', () => show(idx + 1));

setInterval(() => show(idx + 1), 3500);
