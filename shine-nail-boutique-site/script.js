const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.15 });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

const form = document.getElementById('commentForm');
const comments = document.getElementById('comments');
form.addEventListener('submit', (e) => {
  e.preventDefault();
  const name = document.getElementById('name').value.trim();
  const rating = document.getElementById('rating').value;
  const comment = document.getElementById('comment').value.trim();
  if (!name || !rating || !comment) return;

  const el = document.createElement('div');
  el.className = 'comment-item reveal visible';
  el.innerHTML = `<strong>${escapeHTML(name)}</strong> • ${escapeHTML(rating)}<p>${escapeHTML(comment)}</p>`;
  comments.prepend(el);
  form.reset();
});

function escapeHTML(s){
  return s.replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c] || c));
}
