/* Calculadoras do site — sem dependências, tudo no navegador do usuário (nada é enviado). */
(function () {
  'use strict';

  const DIA = 86400000;

  /* "DD/MM/AAAA" -> dias desde 1970 (UTC), sem fuso horário; null se vazia, incompleta ou inexistente */
  function diaDe(valor) {
    const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec((valor || '').trim());
    if (!m) return null;
    const d = +m[1], mes = +m[2], a = +m[3];
    const t = new Date(Date.UTC(a, mes - 1, d));
    if (t.getUTCFullYear() !== a || t.getUTCMonth() !== mes - 1 || t.getUTCDate() !== d) return null;
    return Math.round(t.getTime() / DIA);
  }
  /* campo preenchido por inteiro mas com data que não existe (ex.: 31/02/2026) */
  function dataInvalida(valor) {
    return /^\d{2}\/\d{2}\/\d{4}$/.test((valor || '').trim()) && diaDe(valor) === null;
  }
  function dataDe(dias) {
    const d = new Date(dias * DIA);
    const p = (n) => String(n).padStart(2, '0');
    return `${p(d.getUTCDate())}/${p(d.getUTCMonth() + 1)}/${d.getUTCFullYear()}`;
  }
  function hojeBR() {
    const d = new Date();
    const p = (n) => String(n).padStart(2, '0');
    return `${p(d.getDate())}/${p(d.getMonth() + 1)}/${d.getFullYear()}`;
  }
  /* máscara dd/mm/aaaa: aceita só dígitos e põe as barras sozinha */
  function mascararData(e) {
    const i = e.target;
    if (!i.classList || !i.classList.contains('calc-data')) return;
    const dig = i.value.replace(/\D/g, '').slice(0, 8);
    let v = dig;
    if (dig.length > 4) v = `${dig.slice(0, 2)}/${dig.slice(2, 4)}/${dig.slice(4)}`;
    else if (dig.length > 2) v = `${dig.slice(0, 2)}/${dig.slice(2)}`;
    if (v !== i.value) i.value = v;
  }
  function numero(valor) {
    const t = String(valor || '').trim().replace(',', '.');
    return t === '' ? null : Number(t);
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
    if (!ref.value) ref.value = hojeBR();

    function calcular() {
      const hoje = diaDe(ref.value);
      const saida = [];
      let dumDUM = null, dumUSG = null;
      [['ig-ref', 'de referência'], ['ig-dum', 'da DUM'], ['ig-usg-data', 'da USG']].forEach(([id, nome]) => {
        if (dataInvalida($(id).value)) saida.push(`<p class="calc-erro">A data ${nome} não existe. Confira o dia e o mês.</p>`);
      });

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

    raiz.addEventListener('input', (e) => { mascararData(e); calcular(); });
    $('ig-limpar').addEventListener('click', () => {
      raiz.querySelectorAll('input').forEach((i) => { if (i !== ref) i.value = ''; });
      ref.value = hojeBR();
      calcular();
    });
    calcular();
  }

  /* ---------- Peso fetal estimado (Hadlock 1985) e percentil (Hadlock 1991) ---------- */

  /* Hadlock et al., 1985: log10(PFE em g), medidas em cm. A ordem define a preferência. */
  const FORMULAS = [
    { nome: 'CC, CA, CF e DBP', usa: ['dbp', 'cc', 'ca', 'cf'],
      f: (m) => 1.3596 + 0.0064 * m.cc + 0.0424 * m.ca + 0.174 * m.cf + 0.00061 * m.dbp * m.ca - 0.00386 * m.ca * m.cf },
    { nome: 'CC, CA e CF', usa: ['cc', 'ca', 'cf'],
      f: (m) => 1.326 - 0.00326 * m.ca * m.cf + 0.0107 * m.cc + 0.0438 * m.ca + 0.158 * m.cf },
    { nome: 'DBP, CA e CF', usa: ['dbp', 'ca', 'cf'],
      f: (m) => 1.335 + 0.0316 * m.dbp + 0.0457 * m.ca + 0.1623 * m.cf - 0.0034 * m.ca * m.cf },
    { nome: 'CA e CF', usa: ['ca', 'cf'],
      f: (m) => 1.304 + 0.05281 * m.ca + 0.1938 * m.cf - 0.004 * m.ca * m.cf },
  ];

  /* Hadlock et al., 1991: mediana do peso (g) para a IG em semanas; DP uniforme de 12,7% */
  function medianaHadlock(semanas) {
    return Math.exp(0.578 + 0.332 * semanas - 0.00354 * semanas * semanas);
  }
  /* distribuição normal acumulada (Abramowitz e Stegun 26.2.17) */
  function phi(z) {
    const t = 1 / (1 + 0.2316419 * Math.abs(z));
    const d = 0.3989422804014327 * Math.exp(-z * z / 2);
    const p = d * t * (0.31938153 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))));
    return z > 0 ? 1 - p : p;
  }
  function gramas(g) {
    return Math.round(g).toLocaleString('pt-BR') + ' g';
  }

  function iniciarPFE(raiz) {
    const $ = (id) => raiz.querySelector('#' + id);

    function calcular() {
      const saida = [];
      const m = {}, erros = [];
      [['dbp', 'DBP'], ['cc', 'CC'], ['ca', 'CA'], ['cf', 'CF']].forEach(([k, nome]) => {
        const v = numero($('pfe-' + k).value);
        if (v === null) return;
        if (isNaN(v) || v <= 0 || v > 500) erros.push(`${nome} inválido.`);
        else m[k] = v / 10;      /* mm -> cm */
      });
      erros.forEach((e) => saida.push(`<p class="calc-erro">${e} Informe a medida em milímetros.</p>`));

      const formula = FORMULAS.find((f) => f.usa.every((k) => k in m));
      let pfe = null;
      if (!erros.length && formula) {
        pfe = Math.pow(10, formula.f(m));
        saida.push(`<p><span class="calc-rotulo">PFE</span> <strong>${gramas(pfe)}</strong><br><small>Hadlock 1985, fórmula com ${formula.nome}.</small></p>`);
      } else if (!erros.length && Object.keys(m).length) {
        saida.push('<p class="calc-erro">Informe pelo menos a CA e o CF.</p>');
      }

      const sem = $('pfe-sem').value, dia = $('pfe-dia').value;
      if (sem !== '') {
        const s = parseInt(sem, 10), r = dia === '' ? 0 : parseInt(dia, 10);
        if (isNaN(s) || isNaN(r) || r < 0 || r > 6 || s < 10 || s > 40 || (s === 40 && r > 0)) {
          saida.push('<p class="calc-erro">A curva de Hadlock vai de 10 a 40 semanas: semanas de 10 a 40 e dias de 0 a 6.</p>');
        } else {
          const igSem = s + r / 7, med = medianaHadlock(igSem);
          const p10 = med * (1 - 1.2816 * 0.127), p90 = med * (1 + 1.2816 * 0.127);
          let linha = `<p><span class="calc-rotulo">Curva</span> mediana para ${s}+${r}: <strong>${gramas(med)}</strong> · p10 ${gramas(p10)} · p90 ${gramas(p90)}</p>`;
          if (pfe !== null) {
            const z = (pfe / med - 1) / 0.127, pc = phi(z) * 100;
            const txt = pc < 1 ? '< 1' : pc > 99 ? '> 99' : String(Math.round(pc));
            const faixa = pc < 10 ? ' — abaixo do p10' : pc > 90 ? ' — acima do p90' : '';
            linha = `<p><span class="calc-rotulo">Percentil</span> <strong>${txt}</strong>${faixa}</p>` + linha;
          }
          saida.push(linha);
        }
      }

      $('pfe-resultado').innerHTML = saida.length ? saida.join('')
        : '<p class="calc-vazio">Preencha as medidas e a idade gestacional.</p>';
    }

    raiz.addEventListener('input', calcular);
    $('pfe-limpar').addEventListener('click', () => {
      raiz.querySelectorAll('input').forEach((i) => { i.value = ''; });
      calcular();
    });
    calcular();
  }

  function iniciar() {
    document.querySelectorAll('.calc-ig').forEach(iniciarIG);
    document.querySelectorAll('.calc-pfe').forEach(iniciarPFE);
  }
  if (typeof document$ !== 'undefined') document$.subscribe(iniciar);
  else document.addEventListener('DOMContentLoaded', iniciar);
})();
