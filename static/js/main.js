document.addEventListener('DOMContentLoaded', function() {
    // Handle sidebar menu active state
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll('.sidebar-menu li');
    
    menuItems.forEach(item => {
        const link = item.querySelector('a');
        if (link.getAttribute('href') === currentPath) {
            item.classList.add('active');
        }
    });
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
    
    // Add submit animation to form buttons
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const button = this.querySelector('button[type="submit"]');
            if (button) {
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                button.disabled = true;
            }
        });
    });
    
    // Revenue input formatter
    const revenueInput = document.getElementById('revenue');
    if (revenueInput) {
        revenueInput.addEventListener('blur', function() {
            if (this.value) {
                const numValue = parseFloat(this.value.replace(/,/g, ''));
                if (!isNaN(numValue)) {
                    this.value = numValue;
                }
            }
        });
    }
    
    // Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });
});