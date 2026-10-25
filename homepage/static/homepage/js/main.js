// Текущий год в подвале: значение не записано в HTML, его ставит скрипт.
const yearElement = document.getElementById("current-year");

if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
}

// Подсветка пункта меню текущего раздела. Если подходят несколько
// пунктов (/tickets/ и /tickets/statistics/), выбирается самый точный -
// с самым длинным адресом.
const path = window.location.pathname;
let activeLink = null;

document.querySelectorAll(".site-header .nav-link").forEach((link) => {
    const href = link.getAttribute("href");
    const matches = href === "/" ? path === "/" : path.startsWith(href);
    if (matches && (!activeLink || href.length > activeLink.getAttribute("href").length)) {
        activeLink = link;
    }
});

if (activeLink) {
    activeLink.classList.add("active");
}
