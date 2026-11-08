---
title: Calculadora de peso fetal estimado
descricao: Peso fetal estimado pelas fórmulas de Hadlock (1985) e percentil para a idade gestacional pela curva de Hadlock (1991).
---

# Calculadora de peso fetal estimado

Calcula o peso fetal estimado (PFE) a partir da biometria da ultrassonografia (USG), pelas fórmulas de Hadlock, e o percentil desse peso para a idade gestacional (IG), pela curva de Hadlock. Os dados ficam só no seu navegador: nada é enviado nem guardado.

<div class="calc calc-pfe" markdown="0">
  <fieldset>
    <legend>Biometria (mm)</legend>
    <div class="calc-medidas">
      <label>DBP <input type="text" id="pfe-dbp" inputmode="decimal" autocomplete="off"></label>
      <label>CC <input type="text" id="pfe-cc" inputmode="decimal" autocomplete="off"></label>
      <label>CA <input type="text" id="pfe-ca" inputmode="decimal" autocomplete="off"></label>
      <label>CF <input type="text" id="pfe-cf" inputmode="decimal" autocomplete="off"></label>
    </div>
    <p class="calc-ajuda">DBP: diâmetro biparietal · CC: circunferência cefálica · CA: circunferência abdominal · CF: comprimento do fêmur. CA e CF são obrigatórios; com mais medidas, usa-se a fórmula mais completa.</p>
  </fieldset>
  <fieldset>
    <legend>Idade gestacional no dia do exame</legend>
    <div class="calc-linha">
      <label for="pfe-sem">IG</label>
      <span class="calc-ig-laudo">
        <input type="number" id="pfe-sem" min="10" max="40" inputmode="numeric" placeholder="sem"> +
        <input type="number" id="pfe-dia" min="0" max="6" inputmode="numeric" placeholder="dias">
      </span>
    </div>
    <p class="calc-ajuda">Use a IG da datação adotada (ver <a href="../calculadora-de-idade-gestacional/">Calculadora de idade gestacional</a>), não a IG estimada pela biometria do próprio exame.</p>
  </fieldset>
  <div class="calc-resultado" id="pfe-resultado" aria-live="polite"></div>
  <button type="button" class="md-button" id="pfe-limpar">Limpar</button>
</div>

## Como a conta é feita

### Peso fetal estimado

Hadlock e colaboradores publicaram em 1985 fórmulas que estimam o peso a partir de combinações das medidas, todas em centímetros. A calculadora usa a mais completa possível com as medidas informadas:[^hadlock1985][^dicker]

| Medidas | Fórmula |
|---|---|
| CC, CA, CF e DBP | log₁₀ PFE = 1,3596 + 0,0064 CC + 0,0424 CA + 0,174 CF + 0,00061 DBP × CA − 0,00386 CA × CF |
| CC, CA e CF | log₁₀ PFE = 1,326 − 0,00326 CA × CF + 0,0107 CC + 0,0438 CA + 0,158 CF |
| DBP, CA e CF | log₁₀ PFE = 1,335 + 0,0316 DBP + 0,0457 CA + 0,1623 CF − 0,0034 CA × CF |
| CA e CF | log₁₀ PFE = 1,304 + 0,05281 CA + 0,1938 CF − 0,004 CA × CF |

<small>Fórmulas transcritas de Dicker et al., 2025.[^dicker]</small>

As fórmulas que combinam medidas da cabeça, do abdome e do fêmur são as mais acuradas, com desvio-padrão de 7,5% em relação ao peso real.[^hadlock1985] Em outras palavras, um PFE de 2.000 g corresponde, em cerca de dois terços dos casos, a um peso real entre 1.850 g e 2.150 g.

### Percentil

A curva de Hadlock de 1991 descreve o peso fetal de 10 a 40 semanas: de 35 g com 10 semanas a 3.619 g com 40 semanas, com dispersão uniforme de ±12,7% (1 desvio-padrão) em toda a gestação.[^hadlock1991] A mediana para a IG em semanas é calculada por:[^zhang]

peso (g) = e^(0,578 + 0,332 × IG − 0,00354 × IG²)

O percentil é obtido da distribuição normal, com desvio-padrão de 12,7% da mediana.[^hadlock1991] Pelo mesmo critério, o percentil 10 fica 16,3% abaixo da mediana e o percentil 90 fica 16,3% acima.

> [!warning] Limites
> - A curva de Hadlock foi construída com 392 gestantes, predominantemente brancas e de classe média, nos Estados Unidos.[^hadlock1991] O desempenho das fórmulas varia entre populações.
> - O percentil depende da datação: com IG errada, o percentil está errado.

[^hadlock1985]: Hadlock FP, Harrist RB, Sharman RS, Deter RL, Park SK. Estimation of fetal weight with the use of head, body, and femur measurements: a prospective study. Am J Obstet Gynecol. 1985;151(3):333-7. doi:10.1016/0002-9378(85)90298-4
[^dicker]: Dicker P, Conroy R, McAuliffe F, Geary M, Daly S, Morrison JJ, et al. Accuracy of ultrasound estimation of fetal weight in twin pregnancy. Int J Gynaecol Obstet. 2025;170(1):463-70. doi:10.1002/ijgo.16186
[^hadlock1991]: Hadlock FP, Harrist RB, Martinez-Poyer J. In utero analysis of fetal growth: a sonographic weight standard. Radiology. 1991;181(1):129-33. doi:10.1148/radiology.181.1.1887021
[^zhang]: Zhang J, Mikolajczyk R, Lei X, Sun L, Yu H, Cheng W. An adjustable fetal weight standard for twins: a statistical modeling study. BMC Med. 2015;13:159. doi:10.1186/s12916-015-0401-9
