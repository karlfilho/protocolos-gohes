/* Calculadoras do site — sem dependências, tudo no navegador do usuário (nada é enviado). */
(function () {
  'use strict';

  const DIA = 86400000;

  /* "AAAA-MM-DD" -> dias desde 1970 (UTC), sem fuso horário */
  function diaDe(valor) {
    if (!valor) return null;
    const [a, m, d] = valor.split('-').map(Number);
    if (!a || !m || !d) return null;
    return Math.round(Date.UTC(a, m - 1, d) / DIA);
  }
  function dataDe(dias) {
    const d = new Date(dias * DIA);
    const p = (n) => String(n).padStart(2, '0');
    return `${p(d.getUTCDate())}/${p(d.getUTCMonth() + 1)}/${d.getUTCFullYear()}`;
  }
  function hojeISO() {
    const d = new Date();
    const p = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
  }
  function ig(dias) {
    const s = Math.floor(dias / 7), r = dias % 7;
    const sem = s === 1 ? 'semana' : 'semanas', dia = r === 1 ? 'dia' : 'dias';
    return `<strong>${s} ${sem} e ${r} ${dia}</strong> (${s}+${r})`;
  }

  /* INTERGROWTH-21st (Papageorghiou et al., 2014): IG em dias a partir do CCN em mm, válida de 15 a 95 mm */
  function igPorCCN(ccn) {
    return 40.9041 + 3.21585 * Math.sqrt(ccn) + 0.348956 * ccn;
  }

  function iniciarIG(raiz) {
    const $ = (id) => raiz.querySelector('#' + id);
    const ref = $('ig-ref');
    if (!ref.value) ref.value = hojeISO();

    function calcular() {
      const hoje = diaDe(ref.value);
      const saida = [];
      let dumDUM = null, dumUSG = null;

      /* 1. Pela DUM */
      const dum = diaDe($('ig-dum').value);
      if (dum !== null && hoje !== null) {
        const d = hoje - dum;
        if (d < 0) saida.push('<p class="calc-erro">A DUM é posterior à data de referência.</p>');
        else if (d > 44 * 7) saida.push('<p class="calc-erro">A DUM resulta em mais de 44 semanas. Confira a data.</p>');
        else {
          dumDUM = dum;
          saida.push(`<p><span class="calc-rotulo">Pela DUM</span> ${ig(d)} · DPP <strong>${dataDe(dum + 280)}</strong></p>`);
        }
      }

      /* 2. Pela USG: data do exame + IG no exame (informada ou pelo CCN) */
      const exame = diaDe($('ig-usg-data').value);
      const ccnTxt = $('ig-ccn').value.replace(',', '.');
      const sem = $('ig-usg-sem').value, dia = $('ig-usg-dia').value;
      let igExame = null, origem = '';
      if (ccnTxt !== '') {
        const ccn = parseFloat(ccnTxt);
        if (isNaN(ccn) || ccn < 15 || ccn > 95) {
          saida.push('<p class="calc-erro">O CCN precisa estar entre 15 e 95 mm, a faixa em que a fórmula do INTERGROWTH-21st é válida. Fora dela, use a IG do laudo.</p>');
        } else {
          igExame = Math.round(igPorCCN(ccn));
          origem = `CCN ${ccn.toLocaleString('pt-BR')} mm → ${ig(igExame)} no dia do exame (INTERGROWTH-21st)`;
        }
      } else if (sem !== '') {
        const s = parseInt(sem, 10), r = dia === '' ? 0 : parseInt(dia, 10);
        if (isNaN(s) || isNaN(r) || s < 0 || s > 44 || r < 0 || r > 6) saida.push('<p class="calc-erro">IG do laudo inválida: semanas de 0 a 44 e dias de 0 a 6.</p>');
        else { igExame = s * 7 + r; origem = `IG do laudo: ${ig(igExame)} no dia do exame`; }
      }
      if (igExame !== null) {
        if (exame === null) saida.push('<p class="calc-erro">Informe a data da USG.</p>');
        else if (hoje !== null) {
          const d = hoje - exame + igExame;
          if (exame > hoje) saida.push('<p class="calc-erro">A data da USG é posterior à data de referência.</p>');
          else {
            dumUSG = exame - igExame;
            saida.push(`<p><span class="calc-rotulo">Pela USG</span> ${ig(d)} · DPP <strong>${dataDe(dumUSG + 280)}</strong><br><small>${origem}, em ${dataDe(exame)}.</small></p>`);
          }
        }
      }

      /* 3. Comparação, sem decidir pelo usuário */
      if (dumDUM !== null && dumUSG !== null) {
        const dif = dumUSG - dumDUM;   /* positivo: a DUM dá IG maior que a USG */
        const txt = dif === 0 ? 'As duas datações coincidem.'
          : `A IG pela DUM está <strong>${Math.abs(dif)} ${Math.abs(dif) === 1 ? 'dia' : 'dias'} ${dif > 0 ? 'à frente' : 'atrás'}</strong> da IG pela USG.`;
        saida.push(`<p class="calc-nota">${txt} Qual datação adotar é decisão clínica, registrada no prontuário.</p>`);
      }

      $('ig-resultado').innerHTML = saida.length ? saida.join('')
        : '<p class="calc-vazio">Preencha a DUM, a USG ou as duas.</p>';
    }

    raiz.addEventListener('input', calcular);
    $('ig-limpar').addEventListener('click', () => {
      raiz.querySelectorAll('input').forEach((i) => { if (i !== ref) i.value = ''; });
      ref.value = hojeISO();
      calcular();
    });
    calcular();
  }

  function iniciar() {
    document.querySelectorAll('.calc-ig').forEach(iniciarIG);
  }
  if (typeof document$ !== 'undefined') document$.subscribe(iniciar);
  else document.addEventListener('DOMContentLoaded', iniciar);
})();
