
/* Ajax call to toggle favorites */
document.querySelectorAll('.favorite-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
        const auctionId = btn.dataset.auction;

        fetch(`/favorites/${auctionId}/toggle/`)
            .then(response => response.json())
            .then(data => {
                const icon = btn.querySelector('i');

                if (data.favorite) {
                    icon.classList.remove('bi-bookmark');
                    icon.classList.add('bi-bookmark-fill');
                } else {
                    icon.classList.remove('bi-bookmark-fill');
                    icon.classList.add('bi-bookmark');
                }
            });
    });
});