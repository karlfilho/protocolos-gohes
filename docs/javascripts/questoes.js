/* Questões "Teste seu conhecimento": revela a resposta e o comentário. Nada é registrado nem enviado.
   Cada alternativa é um <button> dentro de um <li> (gerado pelo hooks/wiki.py, função questao);
   o resultado é anunciado ao leitor de tela pelo <p class="quiz-aviso" role="status">. */
(function () {
  'use strict';
  function aviso(quiz) {
    let a = quiz.querySelector('.quiz-aviso');
    if (!a) {     /* página gerada antes da mudança do hook */
      a = document.createElement('p'); a.className = 'quiz-aviso'; a.setAttribute('role', 'status');
      quiz.querySelector('.quiz-alternativas').after(a);
    }
    return a;
  }
  function responder(quiz, escolhida) {
    if (quiz.dataset.respondida) return;
    quiz.dataset.respondida = '1';
    const alts = [...quiz.querySelectorAll('.quiz-alt')];
    alts.forEach((a) => {
      a.setAttribute('aria-disabled', 'true');
      if (a.dataset.certa === '1') a.classList.add('quiz-certa');
    });
    const acertou = escolhida.dataset.certa === '1';
    if (!acertou) escolhida.classList.add('quiz-errada');
    escolhida.classList.add('quiz-escolhida');
    const letra = 'ABCDEFGH'[alts.indexOf(alts.find((a) => a.dataset.certa === '1'))] || '';
    const av = aviso(quiz);
    av.textContent = acertou ? '✓ Resposta correta'
      : `✗ Resposta incorreta: a certa é a alternativa ${letra}, destacada acima`;
    av.classList.toggle('quiz-aviso--erro', !acertou);
    const com = quiz.querySelector('.quiz-comentario');
    if (com) com.hidden = false;
    let refazer = quiz.querySelector('.quiz-refazer');
    if (!refazer) {
      refazer = document.createElement('button');
      refazer.type = 'button'; refazer.className = 'md-button quiz-refazer'; refazer.textContent = 'Tentar de novo';
      refazer.addEventListener('click', () => reiniciar(quiz));
      quiz.append(refazer);
    }
    refazer.hidden = false;
  }
  function reiniciar(quiz) {
    delete quiz.dataset.respondida;
    quiz.querySelectorAll('.quiz-alt').forEach((a) => {
      a.classList.remove('quiz-certa', 'quiz-errada', 'quiz-escolhida');
      a.removeAttribute('aria-disabled');
    });
    aviso(quiz).textContent = '';
    const com = quiz.querySelector('.quiz-comentario'); if (com) com.hidden = true;
    const r = quiz.querySelector('.quiz-refazer'); if (r) r.hidden = true;
    const primeira = quiz.querySelector('.quiz-alt'); if (primeira) primeira.focus();
  }
  function iniciar() {
    document.querySelectorAll('.quiz').forEach((quiz) => {
      if (quiz.dataset.pronto) return;
      quiz.dataset.pronto = '1';
      quiz.querySelectorAll('.quiz-alt').forEach((a) => {
        a.addEventListener('click', () => responder(quiz, a));
      });
    });
  }
  if (typeof document$ !== 'undefined') document$.subscribe(iniciar);
  else document.addEventListener('DOMContentLoaded', iniciar);
})();
