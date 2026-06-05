// Mobile menu toggle
document.getElementById('mobile-menu-btn')?.addEventListener('click', function() {
    document.getElementById('mobile-menu').classList.toggle('hidden');
});

// Update cart badge on page load
function updateCartBadge() {
    fetch('/api/cart/info')
        .then(r => r.json())
        .then(data => {
            const badge = document.getElementById('cart-badge');
            if (badge && data.count > 0) {
                badge.textContent = data.count;
                badge.classList.remove('hidden');
            }
        })
        .catch(() => {});
}
updateCartBadge();

// Show toast notification
function showToast(msg) {
    const t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

// Intercept Add to Cart forms to show toast
document.querySelectorAll('form[action*="/cart/add"]').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const fd = new FormData(this);
        fetch(this.action, { method: 'POST', body: fd })
            .then(r => r.json())
            .then(data => {
                const badge = document.getElementById('cart-badge');
                if (badge) {
                    badge.textContent = data.count;
                    badge.classList.remove('hidden');
                    badge.classList.add('bump');
                    setTimeout(() => badge.classList.remove('bump'), 300);
                }
                showToast('Added to cart!');
            });
    });
});
