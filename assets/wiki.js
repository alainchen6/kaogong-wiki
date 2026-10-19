/* Kaogong wiki: theme, mobile nav, search, copy buttons, TOC highlight. */
;(() => {
  const root = document.documentElement
  const savedTheme = localStorage.getItem('mf-wiki-theme')
  if (savedTheme === 'light' || savedTheme === 'dark') root.dataset.theme = savedTheme

  document.querySelector('[data-theme-toggle]')?.addEventListener('click', () => {
    const next = root.dataset.theme === 'light' ? 'dark' : 'light'
    root.dataset.theme = next
    localStorage.setItem('mf-wiki-theme', next)
  })

  const body = document.body
  document.querySelector('[data-menu-toggle]')?.addEventListener('click', () => body.classList.add('nav-open'))
  document.querySelectorAll('[data-menu-close], .nav-link').forEach((el) =>
    el.addEventListener('click', () => body.classList.remove('nav-open')),
  )

  // Reading progress
  const progress = document.querySelector('.reading-progress span')
  const onScroll = () => {
    if (!progress) return
    const max = document.documentElement.scrollHeight - window.innerHeight
    progress.style.width = `${max > 0 ? Math.min(100, (window.scrollY / max) * 100) : 0}%`
  }
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()

  // Copy code buttons
  document.querySelectorAll('.prose pre').forEach((pre) => {
    const button = document.createElement('button')
    button.className = 'code-copy'
    button.type = 'button'
    button.textContent = '复制'
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(pre.innerText)
        button.textContent = '已复制'
      } catch {
        button.textContent = '复制失败'
      }
      setTimeout(() => { button.textContent = '复制' }, 1600)
    })
    pre.appendChild(button)
  })

  // External links
  document.querySelectorAll('.prose a[href^="http"]').forEach((a) => {
    a.target = '_blank'
    a.rel = 'noreferrer noopener'
  })

  // Active TOC item
  const tocLinks = [...document.querySelectorAll('.toc-list a')]
  if (tocLinks.length) {
    const headings = tocLinks
      .map((a) => document.getElementById(decodeURIComponent(a.hash.slice(1))))
      .filter(Boolean)
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return
          tocLinks.forEach((a) => a.classList.toggle('active', a.hash === `#${entry.target.id}`))
        })
      },
      { rootMargin: '-80px 0px -70% 0px', threshold: 0 },
    )
    headings.forEach((heading) => observer.observe(heading))
  }

  // Search
  const overlay = document.querySelector('[data-search-overlay]')
  const input = document.querySelector('[data-search-input]')
  const results = document.querySelector('[data-search-results]')
  let index = []
  let active = -1

  const escapeHtml = (value) =>
    value.replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch])

  // The build injects the mount prefix so the same file works at /wiki and at
  // a GitHub Pages project path such as /kaogong-wiki/wiki.
  const wikiPrefix = window.__WIKI_PREFIX__ || '/wiki'
  fetch(`${wikiPrefix}/search-index.json`)
    .then((response) => (response.ok ? response.json() : []))
    .then((data) => { index = data })
    .catch(() => { index = [] })

  const openSearch = () => {
    if (!overlay) return
    overlay.hidden = false
    document.body.style.overflow = 'hidden'
    requestAnimationFrame(() => input?.focus())
  }
  const closeSearch = () => {
    if (!overlay) return
    overlay.hidden = true
    document.body.style.overflow = ''
  }
  document.querySelector('[data-search-open]')?.addEventListener('click', openSearch)
  document.querySelector('[data-search-close]')?.addEventListener('click', closeSearch)
  overlay?.addEventListener('click', (event) => {
    if (event.target === overlay) closeSearch()
  })
  document.addEventListener('keydown', (event) => {
    if (event.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName || '')) {
      event.preventDefault()
      openSearch()
    }
    if (event.key === 'Escape') {
      closeSearch()
      body.classList.remove('nav-open')
    }
  })

  const score = (item, q) => {
    const title = item.title.toLowerCase()
    const nav = item.nav.toLowerCase()
    const description = (item.description || '').toLowerCase()
    const text = (item.text || '').toLowerCase()
    let value = 0
    if (title.includes(q)) value += 60
    if (nav.includes(q)) value += 30
    if (description.includes(q)) value += 16
    if (text.includes(q)) value += 8
    return value
  }

  const snippet = (item, q) => {
    const text = item.text || ''
    const position = text.toLowerCase().indexOf(q)
    if (position < 0) return escapeHtml((item.description || '').slice(0, 120))
    const start = Math.max(0, position - 70)
    const end = Math.min(text.length, position + 120)
    const raw = `${start > 0 ? '…' : ''}${text.slice(start, end)}${end < text.length ? '…' : ''}`
    return escapeHtml(raw).replace(new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'ig'), '<mark>$1</mark>')
  }

  const render = () => {
    if (!results) return
    const q = (input?.value || '').trim().toLowerCase()
    active = -1
    if (!q) {
      results.innerHTML = '<p class="search-hint">输入关键词，例如 <kbd>RDF</kbd>、<kbd>EAM</kbd>、<kbd>GCMC</kbd>。</p>'
      return
    }
    const matches = index
      .map((item) => ({ item, score: score(item, q) }))
      .filter((entry) => entry.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 8)
    if (!matches.length) {
      results.innerHTML = '<p class="search-hint">没有找到匹配页面。试试英文关键词或模块名。</p>'
      return
    }
    results.innerHTML = matches
      .map(
        ({ item }) => `<a class="search-result" href="${item.url}">
          <strong>${escapeHtml(item.title)}</strong>
          <span>${escapeHtml(item.section)} · ${escapeHtml(item.nav)}</span>
          <p>${snippet(item, q)}</p>
        </a>`,
      )
      .join('')
    results.querySelectorAll('.search-result').forEach((el, i) => {
      el.addEventListener('mouseenter', () => setActive(i))
    })
  }

  const setActive = (next) => {
    const links = [...(results?.querySelectorAll('.search-result') || [])]
    if (!links.length) return
    active = (next + links.length) % links.length
    links.forEach((link, i) => link.classList.toggle('active', i === active))
    links[active]?.scrollIntoView({ block: 'nearest' })
  }

  input?.addEventListener('input', render)
  input?.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowDown') { event.preventDefault(); setActive(active + 1) }
    if (event.key === 'ArrowUp') { event.preventDefault(); setActive(active - 1) }
    if (event.key === 'Enter') {
      const links = results?.querySelectorAll('.search-result') || []
      if (links[active >= 0 ? active : 0]) window.location.href = links[active >= 0 ? active : 0].href
    }
  })
})()
