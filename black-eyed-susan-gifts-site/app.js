const products=[
{id:1,n:'Signature Gift Box',p:49},{id:2,n:'Seasonal Favorites Bundle',p:65},{id:3,n:'Premium Keepsake Set',p:79},{id:4,n:'Personalized Add-On',p:18},
{id:5,n:'Holiday Collection Pack',p:92},{id:6,n:'Thank-You Mini Bundle',p:35},{id:7,n:'Luxury Wrap Upgrade',p:12},{id:8,n:'Event Gift Suite',p:120}
];
const cart=[];const grid=document.getElementById('grid');const cartEl=document.getElementById('cart');
grid.innerHTML=products.map(p=><article class='product'><small>Featured</small><h3></h3><p class='price'>{p.p}</p><button data-id=''>Add to Cart</button></article>).join('');
function draw(){document.getElementById('count').textContent=cart.reduce((a,b)=>a+b.q,0);const total=cart.reduce((a,b)=>a+b.q*b.p,0);cartEl.innerHTML=(cart.map(i=><div class='line'><span> x</span><strong>{(i.p*i.q).toFixed(2)}</strong></div>).join('')||'<em>Cart empty</em>')+<hr><div class='line'><span>Total</span><strong>{total.toFixed(2)}</strong></div>;}
document.addEventListener('click',e=>{const id=+e.target.dataset.id;if(!id)return;const p=products.find(x=>x.id===id);const hit=cart.find(x=>x.id===id);if(hit)hit.q++;else cart.push({...p,q:1});draw();});
document.getElementById('year').textContent=new Date().getFullYear();draw();
