const services=[
{name:'Classic Manicure',price:25,desc:'Nail shaping, cuticle care, and polish.'},
{name:'Spa Pedicure',price:42,desc:'Exfoliation, massage, and polish finish.'},
{name:'Gel Manicure',price:38,desc:'Long-lasting gel color with glossy finish.'},
{name:'Acrylic Full Set',price:55,desc:'Custom length and shape with polish.'},
{name:'Dip Powder Nails',price:48,desc:'Durable color with lightweight feel.'},
{name:'Custom Nail Art',price:15,desc:'Add-on design pricing starts at.'}
];
const grid=document.getElementById('servicesGrid');
const svc=document.getElementById('svc');
grid.innerHTML=services.map(s=>`<article class="service"><h3>${s.name}</h3><p>${s.desc}</p><p class="price">From $${s.price}</p></article>`).join('');
svc.innerHTML=services.map(s=>`<option>${s.name}</option>`).join('');
document.getElementById('form').addEventListener('submit',e=>{e.preventDefault();const f=new FormData(e.target);document.getElementById('msg').textContent=`Thanks ${f.get('name')} — your ${f.get('service')} request was submitted.`;e.target.reset();});
document.getElementById('year').textContent=new Date().getFullYear();