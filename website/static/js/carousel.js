/*This script makes carousel animation to stop when user hovers over to the component*/

// Get the Carousel element
const carousel = document.querySelector('#carouselExampleCaptions');

// Pause Carousel on hover
carousel.addEventListener('mouseenter', () => {
    carousel.carousel('pause');
});

// Resume Carousel on hover out
carousel.addEventListener('mouseleave', () => {
    carousel.carousel('cycle');
});