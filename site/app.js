const progressBar = document.querySelector('.reading-progress span');
const updateProgress = () => {
  const scrollable = document.documentElement.scrollHeight - innerHeight;
  const progress = scrollable > 0 ? scrollY / scrollable : 0;
  progressBar.style.width = `${Math.min(1, Math.max(0, progress)) * 100}%`;
};

addEventListener('scroll', updateProgress, { passive: true });
addEventListener('resize', updateProgress);
updateProgress();

const links = [...document.querySelectorAll('.chapter-nav a')];
const sections = [...document.querySelectorAll('main section[id]')];

const setCurrent = (id) => {
  links.forEach((link) => {
    const current = link.hash === `#${id}`;
    link.classList.toggle('is-current', current);
    if (current) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
};

if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    const visible = entries.filter((entry) => entry.isIntersecting);
    if (visible.length) setCurrent(visible.at(-1).target.id);
  }, { rootMargin: '-35% 0px -55%', threshold: 0 });
  sections.forEach((section) => observer.observe(section));
}
