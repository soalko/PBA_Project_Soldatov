// Текущий год в подвале: значение не записано в HTML, его ставит скрипт.
const yearElement = document.getElementById("current-year");

if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
}

// Подсветка пункта меню текущего раздела.
const path = window.location.pathname;

document.querySelectorAll(".site-header .nav-link").forEach((link) => {
    const href = link.getAttribute("href");
    const isHome = href === "/";
    if ((isHome && path === "/") || (!isHome && path.startsWith(href))) {
        link.classList.add("active");
    }
});
