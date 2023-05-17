# Projeto de Otimização de Parâmetros em Hidrologia

Este projeto utiliza Python para otimizar os parâmetros de uma equação de hidrologia conhecida como equação de Ven Te Chow. A equação é usada para calcular a intensidade da chuva em diferentes intervalos de tempo e períodos de retorno.

## Contexto

A equação de Ven Te Chow é comumente usada em estudos de hidrologia para modelar a intensidade da chuva. Os parâmetros desta equação podem variar dependendo de diversos fatores, como a localização geográfica e o clima. Portanto, a otimização desses parâmetros é essencial para garantir que a equação forneça as estimativas mais precisas possíveis.

## Metodologia

O projeto emprega diversas bibliotecas Python, incluindo `pandas`, `numpy` e `scipy`. O processo de otimização é realizado usando o algoritmo L-BFGS-B da biblioteca `scipy`.

O código é organizado em várias funções, cada uma com um propósito específico:

- `ventechow_calculations`: Calcula os valores iniciais de intensidade de chuva para diferentes períodos de retorno e intervalos de tempo.
- `transform_dataframe`: Transforma o DataFrame original para facilitar o cálculo do erro relativo.
- `add_condition`: Adiciona uma coluna ao DataFrame com uma condição baseada no intervalo de tempo.
- `calculate_i`: Calcula a intensidade de chuva estimada.
- `apply_i_calculated`: Aplica a equação de
