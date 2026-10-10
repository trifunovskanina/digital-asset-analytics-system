const navbar = document.querySelector('.navbar');
const navToggle = navbar.querySelector('.nav-toggle');

navbar.classList.add('nav-ready');

navToggle.addEventListener('click', () => {
    const open = navbar.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', String(open));
});
