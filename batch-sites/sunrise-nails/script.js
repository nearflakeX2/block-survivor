const reviews=[...document.querySelectorAll('.review')]; let i=0;
function show(n){i=(n+reviews.length)%reviews.length; reviews.forEach((r,x)=>r.classList.toggle('active',x===i));}
document.getElementById('prev').onclick=()=>show(i-1); document.getElementById('next').onclick=()=>show(i+1);
setInterval(()=>show(i+1),3200);
