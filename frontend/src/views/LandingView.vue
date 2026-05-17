<template>
  <div class="landing" :class="theme">
    <!-- Navbar -->
    <nav class="navbar">
      <div class="nav-inner">
        <a class="logo" href="#">Raku<span>sell</span></a>

        <ul class="nav-links">
          <li><a href="#about">{{ t('nav.about') }}</a></li>
          <li><a href="#pricing">{{ t('nav.pricing') }}</a></li>
          <li><a href="#faq">{{ t('nav.faq') }}</a></li>
          <li><a href="#contacts">{{ t('nav.contacts') }}</a></li>
          <li><a href="#label">Label Sorter</a></li>
        </ul>

        <div class="nav-actions">
          <!-- Theme toggle -->
          <button class="icon-btn" @click="toggleTheme" :title="theme === 'dark' ? 'Light mode' : 'Dark mode'">
            <span v-if="theme === 'dark'">☀️</span>
            <span v-else>🌙</span>
          </button>

          <a href="/login" class="btn btn-outline">{{ t('nav.login') }}</a>
          <a href="/login" class="btn btn-primary">{{ t('nav.register') }}</a>

          <!-- Language switcher -->
          <div class="lang-switcher" @click.stop="langOpen = !langOpen">
            <span>{{ currentLang.flag }} {{ currentLang.label }}</span>
            <span class="chevron">▾</span>
            <ul v-if="langOpen" class="lang-dropdown">
              <li v-for="l in langs" :key="l.code" @click="setLang(l.code)">
                {{ l.flag }} {{ l.label }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="hero">
      <!-- Decorative blobs -->
      <div class="blob blob-blue"></div>
      <div class="blob blob-purple"></div>
      <div class="blob blob-pink"></div>
      <div class="blob blob-dark-blue"></div>

      <div class="hero-content">
        <div class="hero-text">
          <h1>
            {{ t('hero.title1') }} <span class="accent-orange">Kaspi</span><br>
            {{ t('hero.title2') }}<br>
            {{ t('hero.title3') }}<br>
            {{ t('hero.title4') }} <span class="accent-orange">{{ t('hero.title5') }}</span>
          </h1>
          <p class="hero-sub">{{ t('hero.sub') }}</p>
          <div class="hero-btns">
            <a href="/login" class="btn btn-primary btn-lg">{{ t('hero.cta1') }}</a>
            <a href="#about" class="btn btn-ghost btn-lg">{{ t('hero.cta2') }}</a>
          </div>
        </div>

        <!-- Phone mockup -->
        <div class="phone-mockup">
          <div class="phone-frame">
            <div class="phone-screen">
              <div class="kaspi-item featured">
                <div class="kaspi-badge">3% Б</div>
                <div class="kaspi-img-placeholder">📱</div>
                <div class="kaspi-verified">✔ Проверен продавцом</div>
                <div class="kaspi-rating">⭐ 4.9 · 183 отзыва</div>
                <div class="kaspi-title">Смартфон Apple iPhone 17 Pro Max 256Gb оранжевый</div>
                <div class="kaspi-shop-row">
                  <div class="kaspi-shop">
                    <strong>Ваш магазин</strong>
                    <span>5.0 ⭐ 16 отзывов</span>
                  </div>
                  <button class="kaspi-btn">Выбрать</button>
                </div>
                <div class="kaspi-price">829 298 ₸</div>
              </div>
              <div class="kaspi-item">
                <div class="kaspi-title">Смартфон</div>
                <div class="kaspi-rating-small">⭐ 4.8 · 151 отзыв</div>
                <div class="kaspi-price-row">
                  <span>829 376 ₸</span>
                  <button class="kaspi-btn">Выбрать</button>
                </div>
              </div>
              <div class="kaspi-item">
                <div class="kaspi-title">Smart Phone</div>
                <div class="kaspi-rating-small">⭐ 4.8 · 39 отзывов</div>
                <div class="kaspi-price-row">
                  <span>829 431 ₸</span>
                  <button class="kaspi-btn">Выбрать</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- WhatsApp button -->
    <a class="whatsapp-btn" href="https://wa.me/77067149599" target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" fill="white" width="28" height="28">
        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
      </svg>
    </a>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Theme
const theme = ref('dark')
function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
}

// i18n
const langs = [
  { code: 'ru', label: 'Русский', flag: '🇷🇺' },
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'kz', label: 'Қазақша', flag: '🇰🇿' },
  { code: 'zh', label: '中文', flag: '🇨🇳' },
]
const lang = ref('ru')
const langOpen = ref(false)
const currentLang = computed(() => langs.find(l => l.code === lang.value))

function setLang(code) {
  lang.value = code
  langOpen.value = false
}

// Close dropdown on outside click
if (typeof window !== 'undefined') {
  window.addEventListener('click', () => { langOpen.value = false })
}

const messages = {
  ru: {
    nav: { about: 'Описание', pricing: 'Тарифы', faq: 'FAQ', contacts: 'Контакты', login: 'Войти', register: 'Зарегистрироваться' },
    hero: {
      title1: 'Ваши товары – в топе',
      title2: 'Автоматизируй',
      title3: 'свой магазин',
      title4: 'и продавай на',
      title5: 'максимуме',
      sub: 'Rakusell — профессиональный инструмент для роста ваших продаж на крупнейшем маркетплейсе Казахстана бот автоснижения и автоповышения цен на товары',
      cta1: 'Попробовать бесплатно 3 дня',
      cta2: 'Подробнее',
    },
  },
  en: {
    nav: { about: 'About', pricing: 'Pricing', faq: 'FAQ', contacts: 'Contacts', login: 'Login', register: 'Sign Up' },
    hero: {
      title1: 'Your products — top of',
      title2: 'Automate',
      title3: 'your store',
      title4: 'and sell at',
      title5: 'maximum',
      sub: 'Rakusell — a professional tool for growing your sales on Kazakhstan\'s largest marketplace. Auto price decrease and increase bot.',
      cta1: 'Try free for 3 days',
      cta2: 'Learn more',
    },
  },
  kz: {
    nav: { about: 'Сипаттама', pricing: 'Тарифтер', faq: 'FAQ', contacts: 'Байланыс', login: 'Кіру', register: 'Тіркелу' },
    hero: {
      title1: 'Тауарларыңыз — топта',
      title2: 'Дүкеніңізді',
      title3: 'автоматтандырыңыз',
      title4: 'және максималды',
      title5: 'сатыңыз',
      sub: 'Rakusell — Қазақстанның ең ірі маркетплейсінде сатылымды арттыруға арналған кәсіби құрал.',
      cta1: '3 күн тегін қолданып көру',
      cta2: 'Толығырақ',
    },
  },
  zh: {
    nav: { about: '介绍', pricing: '价格', faq: '常见问题', contacts: '联系我们', login: '登录', register: '注册' },
    hero: {
      title1: '您的商品排名',
      title2: '自动化',
      title3: '您的店铺',
      title4: '实现最大化',
      title5: '销售',
      sub: 'Rakusell — 哈萨克斯坦最大电商平台的专业销售增长工具，自动调价机器人。',
      cta1: '免费试用3天',
      cta2: '了解更多',
    },
  },
}

function t(key) {
  const keys = key.split('.')
  let val = messages[lang.value]
  for (const k of keys) val = val?.[k]
  return val || key
}
</script>

<style scoped>
/* ===== BASE ===== */
.landing {
  min-height: 100vh;
  font-family: 'Inter', 'Segoe UI', sans-serif;
  position: relative;
  overflow-x: hidden;
}

.landing.dark {
  background: #0d0d1a;
  color: #fff;
}

.landing.light {
  background: #f0f2ff;
  color: #111;
}

/* ===== NAVBAR ===== */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 0 2rem;
  height: 64px;
  display: flex;
  align-items: center;
  backdrop-filter: blur(12px);
  background: rgba(13, 13, 26, 0.7);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.landing.light .navbar {
  background: rgba(240, 242, 255, 0.85);
  border-bottom: 1px solid rgba(0,0,0,0.08);
}

.nav-inner {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.logo {
  font-size: 1.5rem;
  font-weight: 800;
  color: #fff;
  text-decoration: none;
  letter-spacing: -0.5px;
  flex-shrink: 0;
}

.landing.light .logo { color: #111; }

.logo span {
  color: #00d4aa;
}

.nav-links {
  display: flex;
  list-style: none;
  gap: 1.5rem;
  margin: 0;
  padding: 0;
  flex: 1;
}

.nav-links a {
  color: rgba(255,255,255,0.8);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.landing.light .nav-links a { color: rgba(0,0,0,0.7); }

.nav-links a:hover { color: #fff; }
.landing.light .nav-links a:hover { color: #000; }

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

/* ===== BUTTONS ===== */
.btn {
  padding: 0.5rem 1.25rem;
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}

.btn-outline {
  border: 1.5px solid rgba(255,255,255,0.4);
  color: #fff;
  background: transparent;
}

.landing.light .btn-outline {
  border-color: rgba(0,0,0,0.3);
  color: #111;
}

.btn-outline:hover { border-color: #fff; }

.btn-primary {
  background: linear-gradient(135deg, #00d4aa, #00a8ff);
  color: #fff;
  border: none;
}

.btn-primary:hover { opacity: 0.9; transform: translateY(-1px); }

.btn-ghost {
  border: 1.5px solid rgba(255,255,255,0.3);
  color: #fff;
  background: transparent;
}

.landing.light .btn-ghost { border-color: rgba(0,0,0,0.25); color: #111; }

.btn-lg { padding: 0.75rem 1.75rem; font-size: 1rem; }

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 0.25rem;
}

/* ===== LANG SWITCHER ===== */
.lang-switcher {
  position: relative;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.875rem;
  color: rgba(255,255,255,0.8);
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  border: 1.5px solid rgba(255,255,255,0.2);
  user-select: none;
}

.landing.light .lang-switcher { color: rgba(0,0,0,0.7); border-color: rgba(0,0,0,0.2); }

.chevron { font-size: 0.7rem; }

.lang-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: #1a1a2e;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  list-style: none;
  padding: 0.5rem 0;
  margin: 0;
  min-width: 140px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  z-index: 200;
}

.landing.light .lang-dropdown { background: #fff; border-color: rgba(0,0,0,0.1); }

.lang-dropdown li {
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: rgba(255,255,255,0.85);
  transition: background 0.15s;
}

.landing.light .lang-dropdown li { color: #111; }

.lang-dropdown li:hover { background: rgba(255,255,255,0.08); }
.landing.light .lang-dropdown li:hover { background: rgba(0,0,0,0.05); }

/* ===== HERO ===== */
.hero {
  min-height: 100vh;
  padding: 80px 2rem 4rem;
  position: relative;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.hero-content {
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 3rem;
  position: relative;
  z-index: 2;
}

.hero-text {
  flex: 1;
  max-width: 580px;
}

.hero-text h1 {
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800;
  line-height: 1.2;
  margin: 0 0 1.25rem;
}

.accent-orange { color: #ff6b35; }

.hero-sub {
  font-size: 1rem;
  line-height: 1.6;
  color: rgba(255,255,255,0.7);
  margin: 0 0 2rem;
  max-width: 480px;
}

.landing.light .hero-sub { color: rgba(0,0,0,0.6); }

.hero-btns {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

/* ===== BLOBS ===== */
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.55;
  pointer-events: none;
}

.blob-blue {
  width: 380px; height: 380px;
  background: #1a3a8f;
  top: 10%; left: -5%;
}

.blob-purple {
  width: 320px; height: 320px;
  background: #6b21a8;
  top: 20%; left: 20%;
}

.blob-pink {
  width: 280px; height: 280px;
  background: #be185d;
  bottom: 5%; left: 10%;
}

.blob-dark-blue {
  width: 200px; height: 200px;
  background: #1e40af;
  bottom: 20%; right: 35%;
}

/* ===== PHONE MOCKUP ===== */
.phone-mockup {
  flex-shrink: 0;
}

.phone-frame {
  width: 300px;
  background: #111;
  border-radius: 40px;
  padding: 16px;
  box-shadow: 0 0 0 2px #333, 0 32px 80px rgba(0,0,0,0.6);
  position: relative;
}

.phone-frame::before {
  content: '';
  display: block;
  width: 80px;
  height: 10px;
  background: #222;
  border-radius: 999px;
  margin: 0 auto 12px;
}

.phone-screen {
  background: #fff;
  border-radius: 28px;
  overflow: hidden;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.kaspi-item {
  background: #fff;
  border-radius: 8px;
  padding: 8px;
  font-size: 0.75rem;
  color: #111;
  border-bottom: 1px solid #f0f0f0;
}

.kaspi-item.featured {
  background: #f0fff8;
  border: 1.5px solid #00c48c;
}

.kaspi-badge {
  display: inline-block;
  background: #00c48c;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  margin-bottom: 4px;
}

.kaspi-img-placeholder {
  font-size: 2.5rem;
  text-align: center;
  padding: 8px 0;
}

.kaspi-verified {
  color: #00c48c;
  font-size: 0.65rem;
  margin-bottom: 2px;
}

.kaspi-rating { color: #f59e0b; font-size: 0.7rem; margin-bottom: 4px; }
.kaspi-rating-small { color: #f59e0b; font-size: 0.65rem; }

.kaspi-title {
  font-weight: 600;
  font-size: 0.75rem;
  margin-bottom: 4px;
  color: #111;
}

.kaspi-shop-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1.5px solid #f59e0b;
  border-radius: 6px;
  padding: 4px 6px;
  margin-bottom: 4px;
}

.kaspi-shop { display: flex; flex-direction: column; font-size: 0.65rem; }
.kaspi-shop strong { font-size: 0.7rem; }

.kaspi-btn {
  background: #0066ff;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 0.65rem;
  font-weight: 600;
  cursor: pointer;
}

.kaspi-price { font-weight: 700; color: #111; font-size: 0.8rem; }

.kaspi-price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}

/* ===== WHATSAPP BUTTON ===== */
.whatsapp-btn {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  width: 56px;
  height: 56px;
  background: #25d366;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(37, 211, 102, 0.4);
  z-index: 200;
  transition: transform 0.2s;
}

.whatsapp-btn:hover { transform: scale(1.1); }

/* ===== RESPONSIVE ===== */
@media (max-width: 900px) {
  .nav-links { display: none; }
  .hero-content { flex-direction: column; text-align: center; }
  .hero-btns { justify-content: center; }
  .phone-mockup { order: -1; }
  .phone-frame { width: 240px; }
}
</style>
