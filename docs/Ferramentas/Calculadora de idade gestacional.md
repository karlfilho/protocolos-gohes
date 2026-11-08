---
title: Calculadora de idade gestacional
descricao: Idade gestacional e data provável do parto pela DUM, pela USG (IG do laudo ou CCN) ou pelas duas, com a diferença entre elas.
---

# Calculadora de idade gestacional

Calcula a idade gestacional (IG) e a data provável do parto (DPP) pela data da última menstruação (DUM), por uma ultrassonografia (USG) anterior ou pelas duas. Os dados ficam só no seu navegador: nada é enviado nem guardado.

<div class="calc calc-ig" markdown="0">
  <div class="calc-linha">
    <label for="ig-ref">Data de referência</label>
    <input type="text" id="ig-ref" class="calc-data" inputmode="numeric" maxlength="10" placeholder="dd/mm/aaaa" autocomplete="off">
  </div>
  <fieldset>
    <legend>Pela DUM</legend>
    <div class="calc-linha">
      <label for="ig-dum">Data da última menstruação</label>
      <input type="text" id="ig-dum" class="calc-data" inputmode="numeric" maxlength="10" placeholder="dd/mm/aaaa" autocomplete="off">
    </div>
  </fieldset>
  <fieldset>
    <legend>Pela USG</legend>
    <div class="calc-linha">
      <label for="ig-usg-data">Data da USG</label>
      <input type="text" id="ig-usg-data" class="calc-data" inputmode="numeric" maxlength="10" placeholder="dd/mm/aaaa" autocomplete="off">
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
      <input type="text" id="ig-ccn" inputmode="decimal" placeholder="15 a 84">
    </div>
    <p class="calc-ajuda">Informe a primeira USG acurada da gestação. Se o CCN for preenchido, ele é usado no lugar da IG do laudo.</p>
  </fieldset>
  <div class="calc-resultado" id="ig-resultado" aria-live="polite"></div>
  <button type="button" class="md-button" id="ig-limpar">Limpar</button>
</div>

## Como a conta é feita

- **Pela DUM:** a IG é o tempo decorrido desde o primeiro dia da última menstruação. A DPP é a DUM mais 280 dias (40 semanas).[^ms2022]
- **Pela IG do laudo:** a IG do dia do exame é somada ao tempo decorrido desde a USG.
- **Pelo CCN:** a IG do dia do exame é calculada pela fórmula do INTERGROWTH-21st, IG (dias) = 40,9041 + 3,21585 × √CCN + 0,348956 × CCN, com o CCN em milímetros.[^papageorghiou] A calculadora aceita CCN de 15 a 84 mm. A fórmula não vale abaixo de 15 mm.[^papageorghiou] Acima de 84 mm (cerca de 14 semanas), o CCN perde precisão, e a datação deve usar outras medidas.[^acog700] Ver [[Ultrassonografia da gestação inicial]].

## DUM ou USG?

A medida do embrião ou do feto no primeiro trimestre, até 13+6 semanas, é o método mais preciso para estabelecer ou confirmar a IG. Pelo CCN, a precisão é de ±5 a 7 dias, e é maior quanto mais cedo o exame. O diâmetro médio do saco gestacional não deve ser usado para datar.[^acog700]

Quando a datação pela USG e a pela DUM divergem, a calculadora aplica a tabela de redatação do American College of Obstetricians and Gynecologists (ACOG). A faixa é definida pela IG calculada pela DUM no dia da USG:[^acog700]

| IG pela DUM no dia da USG | Medida | Redatar pela USG se a diferença passar de |
|---|---|---|
| Até 8+6 | CCN | 5 dias |
| 9+0 a 13+6 | CCN | 7 dias |
| 14+0 a 15+6 | DBP, CC, CA, CF | 7 dias |
| 16+0 a 21+6 | DBP, CC, CA, CF | 10 dias |
| 22+0 a 27+6 | DBP, CC, CA, CF | 14 dias |
| 28+0 ou mais | DBP, CC, CA, CF | 21 dias |

<small>Fonte: ACOG, Committee Opinion 700, 2017.[^acog700]</small>

Outras orientações da ACOG:[^acog700]

- Diferenças menores que o limite também podem justificar a redatação, conforme a IG em que a USG foi feita e a confiabilidade da DUM.
- Se a DUM for incerta, a datação se baseia na USG, de preferência até 13+6 semanas e priorizando o exame mais precoce com CCN.
- Se já houve uma USG de primeiro trimestre, sobretudo coerente com a DUM, a IG não deve ser ajustada por um exame do segundo trimestre.
- No terceiro trimestre, redatar arrisca mascarar um feto pequeno, com restrição de crescimento. A decisão exige avaliar o quadro clínico completo e vigilância próxima.
- Na gestação por reprodução assistida, a data provável do parto vem da idade do embrião e da data da transferência. Por exemplo, para um embrião de 5 dias, ela fica 261 dias após a transferência.
- Definida a data provável do parto, ela deve ser discutida com a gestante e registrada em prontuário, e só deve ser mudada em circunstâncias raras. A gestação sem USG que confirme ou revise a data antes de 22 semanas é considerada datada de forma subótima.

## No HES

- No protocolo [[Perda gestacional precoce]], a indicação da imunoglobulina anti-D usa a IG pela USG: só a partir de 12 semanas completas ([[Perda gestacional precoce#4.8. Medidas para todas as pacientes|item 4.8]]).

[^ms2022]: Brasil. Ministério da Saúde. Secretaria de Atenção Primária à Saúde. Manual de gestação de alto risco. Brasília: Ministério da Saúde; 2022.
[^papageorghiou]: Papageorghiou AT, Kennedy SH, Salomon LJ, Ohuma EO, Cheikh Ismail L, Barros FC, et al. International standards for early fetal size and pregnancy dating based on ultrasound measurement of crown-rump length in the first trimester of pregnancy. Ultrasound Obstet Gynecol. 2014;44(6):641-8. doi:10.1002/uog.13448
[^acog700]: American College of Obstetricians and Gynecologists. Committee Opinion No 700: methods for estimating the due date. Obstet Gynecol. 2017;129(5):e150-4. doi:10.1097/AOG.0000000000002046
