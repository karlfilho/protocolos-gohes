/* Menu de temas do cabeçalho (overrides/partials/palette.html). */
(function () {
  'use strict';
  function iniciar() {
    const menu = document.querySelector('.tema-menu');
    if (!menu || menu.dataset.pronto) return;
    menu.dataset.pronto = '1';
    const botao = menu.querySelector('.tema-botao');
    const lista = menu.querySelector('.tema-lista');
    const itens = [...menu.querySelectorAll('.tema-item')];
    const radios = [...document.querySelectorAll('input[name="__palette"]')];

    function marcar() {
      const atual = radios.findIndex((r) => r.checked);
      itens.forEach((b, i) => b.setAttribute('aria-pressed', String(i === atual)));
    }
    function abrir(sim) {
      lista.hidden = !sim;
      botao.setAttribute('aria-expanded', String(sim));
      if (sim) { marcar(); (itens.find((b) => b.getAttribute('aria-pressed') === 'true') || itens[0]).focus(); }
    }
    botao.addEventListener('click', () => abrir(lista.hidden));
    itens.forEach((b) => b.addEventListener('click', () => {
      const r = radios[+b.dataset.tema];
      if (r && !r.checked) r.click();
      abrir(false); botao.focus();
    }));
    lista.addEventListener('keydown', (e) => {
      const i = itens.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') { e.preventDefault(); itens[(i + 1) % itens.length].focus(); }
      if (e.key === 'ArrowUp') { e.preventDefault(); itens[(i - 1 + itens.length) % itens.length].focus(); }
    });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !lista.hidden) { abrir(false); botao.focus(); } });
    document.addEventListener('click', (e) => { if (!menu.contains(e.target)) abrir(false); });
    radios.forEach((r) => r.addEventListener('change', marcar));
    /* migração única: a escolha salva no esquema antigo (automático, claro, escuro; cor "custom")
       apontaria para outro tema na lista nova. Escuro -> Tokyo Night; claro -> Nord. */
    try {
      const chave = Object.keys(localStorage).find((k) => k.endsWith('__palette'));
      const salvo = chave && JSON.parse(localStorage.getItem(chave));
      if (salvo && salvo.color && salvo.color.primary === 'custom') {
        const destino = salvo.color.media === '(prefers-color-scheme)' ? 0 : salvo.color.scheme === 'slate' ? 3 : 1;
        if (radios[destino]) radios[destino].click();
      }
    } catch (e) { /* armazenamento indisponível: nada a migrar */ }
    marcar();
  }
  if (typeof document$ !== 'undefined') document$.subscribe(iniciar);
  else document.addEventListener('DOMContentLoaded', iniciar);
})();
