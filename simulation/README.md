# 시뮬레이션 프로그램 사용법

이 프로그램은 Elliot fitting에서 얻은 파라미터 값을 입력받아 해당하는 스펙트럼 그래프를 생성합니다.

## 실행 방법

```bash
cd simulation
python simulation.py
```

## 파라미터 설명

프로그램 실행 시 다음 파라미터들을 입력할 수 있습니다:

1. **Eg (Band gap energy)**: 밴드갭 에너지 (eV 단위)
   - 기본값: 2.62 eV

2. **Eb (Exciton binding energy)**: 엑시톤 결합 에너지 (meV 단위로 입력, 내부적으로 eV로 변환)
   - 기본값: 50 meV
   - 실제 Ground State Binding Energy는 `Eb / (1-q)^2`로 계산됩니다.

3. **Gamma (Linewidth)**: 선폭 (meV 단위로 입력, 내부적으로 eV로 변환)
   - 기본값: 100 meV

4. **ucvsq (Transition dipole moment squared)**: 전이 쌍극자 모멘트의 제곱
   - 기본값: 10

5. **mhcnp (Mass parameter)**: 질량 파라미터
   - 기본값: 0.060

6. **q (Fractional dimension parameter)**: 분수 차원 파라미터
   - 기본값: 0.2
   - 0: bulk (3D)
   - 0.5-0.6: quasi-2D
   - 1.5: strong QD
   - Effective dimension: Deff = 3 - 2*q

## 출력

프로그램은 두 개의 그래프를 생성합니다:

1. **Energy vs Absorption**: 에너지(eV)를 x축으로 하는 그래프
2. **Wavelength vs Absorption**: 파장(nm)을 x축으로 하는 그래프 (역순으로 표시)

각 그래프에는 다음이 표시됩니다:
- Total (Exciton + Band): 전체 흡수 스펙트럼
- Exciton: 엑시톤 기여
- Band: 밴드 기여
- Eg: 밴드갭 위치

## 결과 저장

프로그램 종료 시 결과를 저장할지 물어봅니다:
- `y` 또는 `yes`: 결과 저장
- `n` 또는 Enter: 저장하지 않음

저장되는 파일:
- `simulation_result.pdf`: 그래프 (PDF 형식)
- `simulation_result.csv`: 데이터 (CSV 형식)

## 예시

```bash
$ python simulation.py

============================================================
피팅 파라미터 입력
============================================================

기본값을 사용하려면 Enter를 누르세요.

Eg (Band gap energy, eV) [기본값: 2.62]: 2.65
Eb (Exciton binding energy, meV) [기본값: 50]: 60
Gamma (Linewidth, meV) [기본값: 100]: 120
ucvsq (Transition dipole moment squared) [기본값: 10]: 12
mhcnp (Mass parameter) [기본값: 0.060]: 0.065
q (Fractional dimension, 0=bulk, 0.5-0.6=quasi-2D, 1.5=strong QD) [기본값: 0.2]: 0.25
```

## 주의사항

- 모든 입력은 숫자여야 합니다.
- 에너지 범위는 Eg 주변으로 적절히 설정하는 것이 좋습니다 (기본값: Eg ± 0.8 eV).
- 파장 그래프는 내림차순으로 표시됩니다 (짧은 파장이 왼쪽).
