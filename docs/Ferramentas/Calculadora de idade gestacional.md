---
title: Calculadora de idade gestacional
descricao: Idade gestacional e data provável do parto pela DUM, pela USG (IG do laudo ou CCN) ou pelas duas, com a diferença entre elas.
---

# Calculadora de idade gestacional

Calcula a idade gestacional (IG) e a data provável do parto (DPP) pela data da última menstruação (DUM), por uma ultrassonografia (USG) anterior ou pelas duas. Os dados ficam só no seu navegador: nada é enviado nem guardado.

<div class="calc calc-ig" markdown="0">
  <div class="calc-linha">
    <label for="ig-ref">Data de referência</label>
    <input type="date" id="ig-ref">
  </div>
  <fieldset>
    <legend>Pela DUM</legend>
    <div class="calc-linha">
      <label for="ig-dum">Data da última menstruação</label>
      <input type="date" id="ig-dum">
    </div>
  </fieldset>
  <fieldset>
    <legend>Pela USG</legend>
    <div class="calc-linha">
      <label for="ig-usg-data">Data da USG</label>
      <input type="date" id="ig-usg-data">
    </div>
    <div class="calc-linha">
      <label for="ig-usg-sem">IG no laudo</label>
      <span class="calc-ig-laudo">
        <input type="number" id="ig-usg-sem" min="0" max="44" inputmode="numeric" placeholder="sem"> +
        <input type="number" id="ig-usg-dia" min="0" max="6" inputmode="numeric" placeholder="dias">
      </span>
    </div>
    <div class="calc-linha">
      <label for="ig-ccn">ou CCN (mm)</label>
      <input type="text" id="ig-ccn" inputmode="decimal" placeholder="15 a 95">
    </div>
    <p class="calc-ajuda">Se o CCN for preenchido, ele é usado no lugar da IG do laudo.</p>
  </fieldset>
  <div class="calc-resultado" id="ig-resultado" aria-live="polite"></div>
  <button type="button" class="md-button" id="ig-limpar">Limpar</button>
</div>

## Como a conta é feita

- **Pela DUM:** a IG é o tempo decorrido desde o primeiro dia da última menstruação. A DPP é a DUM mais 280 dias (40 semanas).[^ms2022]
- **Pela IG do laudo:** a IG do dia do exame é somada ao tempo decorrido desde a USG.
- **Pelo CCN:** a IG do dia do exame é calculada pela fórmula do INTERGROWTH-21st, IG (dias) = 40,9041 + 3,21585 × √CCN + 0,348956 × CCN, com o CCN em milímetros. A fórmula vale para CCN de 15 a 95 mm.[^papageorghiou] Entre 9 e 13 semanas, o CCN cresce rápido e varia pouco entre gestações da mesma idade, o que torna a datação precisa.[^papageorghiou] Ver [[Ultrassonografia da gestação inicial]].

## DUM ou USG?

A calculadora mostra a diferença entre as duas datações, mas não escolhe por você. O American College of Obstetricians and Gynecologists recomenda definir a IG e a DPP assim que houver a DUM, a primeira USG acurada ou ambas. A data assim definida deve ser registrada em prontuário e só deve ser mudada em circunstâncias raras. A gestação sem USG que confirme ou revise a DPP antes de 22 semanas é considerada datada de forma subótima.[^acog700]

## No HES

- No protocolo [[Perda gestacional precoce]], a indicação da imunoglobulina anti-D usa a IG pela USG: só a partir de 12 semanas completas ([[Perda gestacional precoce#4.8. Medidas para todas as pacientes|item 4.8]]).

[^ms2022]: Brasil. Ministério da Saúde. Secretaria de Atenção Primária à Saúde. Manual de gestação de alto risco. Brasília: Ministério da Saúde; 2022.
[^papageorghiou]: Papageorghiou AT, Kennedy SH, Salomon LJ, Ohuma EO, Cheikh Ismail L, Barros FC, et al. International standards for early fetal size and pregnancy dating based on ultrasound measurement of crown-rump length in the first trimester of pregnancy. Ultrasound Obstet Gynecol. 2014;44(6):641-8. doi:10.1002/uog.13448
[^acog700]: American College of Obstetricians and Gynecologists. Committee Opinion No 700: methods for estimating the due date. Obstet Gynecol. 2017;129(5):e150-4. doi:10.1097/AOG.0000000000002046
