/*This script makes animations play when a component enters to viewpoint*/
const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate');
            observer.unobserve(entry.target);
        }
    });
});

const cards = document.querySelectorAll('.card');
cards.forEach(card => {
    observer.observe(card);
});

const headers = document.querySelectorAll('h1');
headers.forEach(header => {
    observer.observe(header);
});