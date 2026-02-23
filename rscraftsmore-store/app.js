const products = [
  { id: 1, name: 'Personalized Stainless Tumbler', price: 28, category: 'Drinkware', emoji: '🥤' },
  { id: 2, name: 'Custom Family Name Sign', price: 64, category: 'Home Decor', emoji: '🏡' },
  { id: 3, name: 'Soy Candle Duo Gift Set', price: 36, category: 'Candles', emoji: '🕯️' },
  { id: 4, name: 'Handmade Welcome Wreath', price: 52, category: 'Seasonal', emoji: '🌿' },
  { id: 5, name: 'Monogram Canvas Tote', price: 24, category: 'Accessories', emoji: '👜' },
  { id: 6, name: 'Bridal Party Gift Box', price: 79, category: 'Gift Sets', emoji: '🎁' },
  { id: 7, name: 'Custom Keychain Set (4)', price: 18, category: 'Accessories', emoji: '🔑' },
  { id: 8, name: 'Event Favor Mini Candles (12)', price: 58, category: 'Candles', emoji: '✨' }
];

const filters = ['All', ...new Set(products.map(p => p.category))];
const grid = document.getElementById('productGrid');
const filtersWrap = document.getElementById('filters');
const cart = [];

function money(n) { return `$${n.toFixed(2)}`; }

function renderFilters(active = 'All') {
  filtersWrap.innerHTML = filters.map(f => `<button class="${f === active ? 'active' : ''}" data-filter="${f}">${f}</button>`).join('');
}

function renderProducts(active = 'All') {
  const list = active === 'All' ? products : products.filter(p => p.category === active);
  grid.innerHTML = list.map(p => `
    <article class="product">
      <div class="img">${p.emoji}</div>
      <div class="content">
        <small>${p.category}</small>
        <h4>${p.name}</h4>
        <div class="price">${money(p.price)}</div>
        <button data-add="${p.id}">Add to Cart</button>
      </div>
    </article>
  `).join('');
}

function renderCart() {
  const wrap = document.getElementById('cartItems');
  const subtotal = cart.reduce((s, i) => s + i.price * i.qty, 0);
  document.getElementById('subtotal').textContent = money(subtotal);
  document.getElementById('cartCount').textContent = cart.reduce((s, i) => s + i.qty, 0);

  wrap.innerHTML = cart.length
    ? cart.map(i => `<div class="cart-item"><strong>${i.name}</strong><br><small>${i.qty} × ${money(i.price)}</small></div>`).join('')
    : '<p>Your cart is empty.</p>';
}

document.addEventListener('click', (e) => {
  const f = e.target.dataset.filter;
  if (f) {
    renderFilters(f);
    renderProducts(f);
  }

  const id = Number(e.target.dataset.add);
  if (id) {
    const p = products.find(x => x.id === id);
    const hit = cart.find(x => x.id === id);
    if (hit) hit.qty++;
    else cart.push({ ...p, qty: 1 });
    renderCart();
  }
});

document.getElementById('cartBtn').onclick = () => document.getElementById('cart').classList.add('open');
document.getElementById('closeCart').onclick = () => document.getElementById('cart').classList.remove('open');
document.getElementById('year').textContent = new Date().getFullYear();

renderFilters();
renderProducts();
renderCart();
