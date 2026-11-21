/* Tabelas largas: o Material as põe num contêiner com rolagem lateral (.md-typeset__scrollwrap).
   Quando a tabela não cabe na tela, o contêiner fica focável e nomeado, para rolar pelo teclado. */
(function () {
  'use strict';
  function nome(caixa) {
    let ant = caixa.previousElementSibling;
    if (ant && ant.classList.contains('tabela-rola')) ant = ant.previousElementSibling;
    const t = ant && ant.textContent.trim();
    return t && /^(Quadro|Tabela)\b/.test(t) ? t : 'Tabela';
  }
  function ajustar() {
    document.querySelectorAll('.md-typeset__scrollwrap').forEach((caixa) => {
      if (caixa.scrollWidth > caixa.clientWidth + 1) {
        caixa.tabIndex = 0;
        caixa.setAttribute('role', 'region');
        caixa.setAttribute('aria-label', nome(caixa) + ' (role para o lado)');
        if (!(caixa.previousElementSibling || {}).classList?.contains('tabela-rola')) {
          const aviso = document.createElement('p');          /* aviso visível; o leitor de tela já ouve o rótulo */
          aviso.className = 'tabela-rola'; aviso.setAttribute('aria-hidden', 'true');
          aviso.textContent = '↔ Deslize para o lado para ver a tabela inteira';
          caixa.before(aviso);
        }
      } else {
        caixa.removeAttribute('tabindex'); caixa.removeAttribute('role'); caixa.removeAttribute('aria-label');
        const ant = caixa.previousElementSibling;
        if (ant && ant.classList.contains('tabela-rola')) ant.remove();
      }
    });
  }
  let espera;
  window.addEventListener('resize', () => { clearTimeout(espera); espera = setTimeout(ajustar, 200); });
  if (typeof document$ !== 'undefined') document$.subscribe(ajustar);
  else document.addEventListener('DOMContentLoaded', ajustar);
})();
