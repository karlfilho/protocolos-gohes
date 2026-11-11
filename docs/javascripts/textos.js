/* Textos-padrão: botão "Copiar" em cada quadro. Nada é enviado. */
(function () {
  'use strict';
  async function copiar(texto) {
    try { await navigator.clipboard.writeText(texto); return true; } catch (e) { /* cai no método antigo */ }
    const area = document.createElement('textarea');
    area.value = texto; area.setAttribute('readonly', ''); area.style.position = 'fixed'; area.style.opacity = '0';
    document.body.append(area); area.select();
    let ok = false; try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    area.remove(); return ok;
  }
  function iniciar() {
    document.querySelectorAll('.texto-padrao').forEach((caixa) => {
      if (caixa.dataset.pronto) return;
      caixa.dataset.pronto = '1';
      const pre = caixa.querySelector('.tp-texto');
      const botao = document.createElement('button');
      botao.type = 'button'; botao.className = 'md-button tp-copiar'; botao.textContent = 'Copiar texto';
      botao.addEventListener('click', async () => {
        const ok = await copiar(pre.textContent);
        botao.textContent = ok ? 'Copiado ✓' : 'Não foi possível copiar: selecione o texto';
        botao.classList.toggle('tp-copiado', ok);
        setTimeout(() => { botao.textContent = 'Copiar texto'; botao.classList.remove('tp-copiado'); }, 2500);
      });
      caixa.prepend(botao);
    });
  }
  if (typeof document$ !== 'undefined') document$.subscribe(iniciar);
  else document.addEventListener('DOMContentLoaded', iniciar);
})();
