/* Questões "Teste seu conhecimento": revela a resposta e o comentário. Nada é registrado nem enviado. */
(function () {
  'use strict';
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
    const com = quiz.querySelector('.quiz-comentario');
    if (com) {
      let aviso = com.querySelector('.quiz-aviso');
      if (!aviso) { aviso = document.createElement('p'); aviso.className = 'quiz-aviso'; com.prepend(aviso); }
      aviso.textContent = acertou ? '✓ Resposta correta' : '✗ Resposta incorreta: a alternativa certa está destacada';
      aviso.classList.toggle('quiz-aviso--erro', !acertou);
      com.hidden = false;
    }
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
    const com = quiz.querySelector('.quiz-comentario'); if (com) com.hidden = true;
    const r = quiz.querySelector('.quiz-refazer'); if (r) r.hidden = true;
    const primeira = quiz.querySelector('.quiz-alt'); if (primeira) primeira.focus();
  }
  function iniciar() {
    document.querySelectorAll('.quiz').forEach((quiz) => {
      if (quiz.dataset.pronto) return;
      quiz.dataset.pronto = '1';
      quiz.querySelectorAll('.quiz-alt').forEach((a) => {
        a.addEventListener('click', (e) => { if (!e.target.closest('a')) responder(quiz, a); });
        a.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); responder(quiz, a); }
        });
      });
    });
  }
  if (typeof document$ !== 'undefined') document$.subscribe(iniciar);
  else document.addEventListener('DOMContentLoaded', iniciar);
})();
