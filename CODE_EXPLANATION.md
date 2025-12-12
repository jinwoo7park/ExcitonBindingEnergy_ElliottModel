# Elliot Fitting 코드 설명서

## 1. 과학적 배경 (Scientific Background)

### 1.1 Elliot Theory 개요

이 코드는 **Elliot Theory**를 기반으로 반도체 및 나노구조 물질의 광학 흡수 스펙트럼을 분석합니다. Elliot Theory는 1957년 R. J. Elliot에 의해 제안된 이론으로, 반도체에서 발생하는 exciton과 band-to-band 전이를 통합적으로 설명합니다.

### 1.2 Exciton (엑시톤)

**Exciton**은 전자(electron)와 정공(hole)이 쿨롱 상호작용으로 결합하여 형성된 준입자(quasiparticle)입니다. 반도체에서 광흡수 시 생성된 전자-정공 쌍이 결합하여 exciton을 형성할 수 있으며, 이는 band gap보다 낮은 에너지에서 흡수가 발생하게 만듭니다.

- **Exciton Binding Energy (Eb)**: Exciton을 분리하는데 필요한 에너지
- **Exciton Series**: 양자수 n=1, 2, 3, ...에 해당하는 이산적인 에너지 준위
- **Ground State (n=1)**: 가장 낮은 에너지 상태의 exciton

### 1.3 Band-to-Band 전이

Band gap 에너지(Eg) 이상의 에너지에서는 전자가 가전자대(valence band)에서 전도대(conduction band)로 직접 전이할 수 있습니다. 이를 **band-to-band transition** 또는 **continuum transition**이라고 합니다.

### 1.4 F-sum Rule

**F-sum rule**은 전기 쌍극자 전이(electric dipole transition)의 oscillator strength에 대한 합 규칙입니다. 이 코드에서는 F-sum rule을 활용하여 exciton과 band 전이의 상대적 기여도를 정량적으로 분석합니다.

### 1.5 Fractional Dimension (q parameter)

나노구조 물질에서는 양자 구속(quantum confinement) 효과로 인해 유효 차원(effective dimension)이 변화합니다:

- **q = 0**: Bulk (3차원) - 전통적인 3D 반도체
- **q = 0.5-0.6**: Quasi-2D - 양자우물(quantum well) 구조
- **q = 1.5**: Strong Quantum Dot (QD) - 강한 구속을 받는 양자점

**Effective Dimension**: Deff = 3 - 2q

q 값이 클수록 양자 구속이 강해지며, exciton binding energy가 증가합니다.

### 1.6 물리적 파라미터

코드에서 피팅하는 주요 파라미터:

1. **Eg (Band Gap Energy)**: 전도대와 가전자대 사이의 에너지 차이 (eV)
2. **Eb (Exciton Binding Energy)**: Exciton을 분리하는데 필요한 에너지 (eV 또는 meV)
   - 실제 Ground State Binding Energy = Eb / (1-q)²
3. **Gamma (Linewidth)**: 스펙트럼 선폭, 불순물/온도 등에 의한 broadening (eV 또는 meV)
4. **ucvsq**: Transition dipole moment squared (전이 쌍극자 모멘트의 제곱)
5. **mhcnp**: Mass parameter (유효 질량 관련 파라미터)
6. **q**: Fractional dimension parameter (0 ~ 1.5)

## 2. 코드 구조 및 기능

### 2.1 주요 모듈

#### `fsum2d.py` - 핵심 계산 모듈

**기능**: F-sum rule을 사용한 흡수 스펙트럼 계산

**주요 함수**:
- `fsum2d(params, xdata, ydata)`: 벡터화된 최적화 버전
- `fsum2d_slow(params, xdata, ydata)`: 원본 MATLAB 구현과 동일한 버전

**계산 과정**:
1. **Exciton 기여도 계산**: n=1부터 50까지의 exciton 상태 합산
   ```
   Enx = Eg - Eb/(n-q)²
   Exciton contribution ∝ Σ [2Eb/(n-q)³] × [1/cosh((E-Enx)/Gamma)]
   ```

2. **Band 기여도 계산**: Eg부터 2Eg까지 적분
   ```
   Band contribution ∝ ∫ [1/cosh((E-E')/Gamma)] × [(1+b)/(1-exp(-2π√(Eb/(E'-Eg))))] dE'
   ```
   여기서 b = 10×mhcnp×(E'-Eg) + 126×mhcnp²×(E'-Eg)²

3. **최종 흡수 스펙트럼**:
   ```
   Absorption = ucvsq × √Eb × (Exciton + Band)
   ```

#### `fitter.py` - 피팅 메인 모듈

**클래스**: `FSumFitter`

**주요 메서드**:

1. **`__init__(deltaE, NS, fitmode)`**
   - `deltaE`: 정규화 에너지 오프셋
   - `NS`: Spline 보간 포인트 수
   - `fitmode`: Baseline 피팅 모드
     - 0: Baseline 없음
     - 1: 선형 baseline
     - 2: Rayleigh scattering (E⁴) baseline

2. **`fit_baseline(xdata, ydata, baseline_mask)`**
   - 사용자가 선택한 구간에서 baseline 피팅
   - fitmode에 따라 선형 또는 E⁴ 함수로 피팅

3. **`select_baseline_mask_interactive(xdata, ydata, fitmode)`**
   - 그래픽 인터페이스로 baseline 및 피팅 범위 선택
   - 사용자가 클릭으로 구간 지정

4. **`fit_data(xdata, ydata, start_point, bounds)`**
   - L-BFGS-B 최적화 알고리즘 사용
   - SSE (Sum of Squared Errors) 최소화
   - 동적 경계값 설정 (Eg ± 0.4 eV)

5. **`process_file(filename, ...)`**
   - 파일 읽기 및 전처리
   - 다중 데이터셋 처리 지원
   - 자동 bandgap 탐지
   - Bandgap-focused 피팅 (Eg ± 0.5 eV)

6. **`calculate_urbach_energy(xdata, ydata, Eb, Eg)`**
   - Urbach tail 분석
   - 지수 감쇠 꼬리 부분의 기울기 계산

7. **`save_results(results, output_dir)`**
   - CSV 형식으로 결과 저장
   - 파라미터 및 피팅 곡선 데이터 포함

8. **`plot_results(results, save_path)`**
   - 피팅 결과 시각화
   - Raw data, Baseline, Exciton, Band, Total 곡선 표시

#### `simulation/simulation.py` - 시뮬레이션 모듈

**기능**: 주어진 파라미터로 이론적 흡수 스펙트럼 생성

**주요 함수**:
- `get_parameter_input()`: 사용자로부터 파라미터 입력 받기
- `simulate_spectrum(params, energy_min, energy_max)`: 스펙트럼 시뮬레이션
- `plot_simulation(...)`: 시뮬레이션 결과 그래프 생성
- `save_simulation_data(...)`: 시뮬레이션 데이터 CSV 저장

**사용 목적**:
- 파라미터 변화에 따른 스펙트럼 변화 예측
- 실험 데이터와 이론 곡선 비교
- 교육 및 이해도 향상

#### `analyze.py` - 간편 분석 스크립트

**기능**: 명령줄에서 간단하게 파일 분석

**사용법**:
```bash
python3 analyze.py data.txt --fitmode 2 --datasets 1,2,3
```

### 2.2 데이터 처리 흐름

```
1. 파일 읽기
   ↓
2. 파장(nm) → 에너지(eV) 변환: E = 1239.84193 / λ
   ↓
3. Baseline 선택 (사용자 인터랙티브 또는 자동)
   ↓
4. Baseline 제거: Cleaned Data = Raw Data - Baseline
   ↓
5. 초기 Bandgap 탐지 (cleaned data에서 threshold 기반)
   ↓
6. 예비 피팅 (전체 범위)
   ↓
7. Bandgap-focused 피팅 (Eg ± 0.5 eV, 선택적)
   ↓
8. 최종 파라미터 추출
   ↓
9. Exciton/Band 분리 계산
   ↓
10. Urbach energy 계산
   ↓
11. 결과 저장 및 시각화
```

## 3. 주요 알고리즘 및 수식

### 3.1 Exciton 스펙트럼

n번째 exciton 상태의 에너지:
```
Enx = Eg - Eb/(n-q)²
```

Exciton 기여도:
```
a_exciton(E) = Σ(n=1 to 50) [2Eb/(n-q)³] × [1/cosh((E-Enx)/Gamma)]
```

### 3.2 Band-to-Band 스펙트럼

Band 기여도 (적분 형태):
```
a_band(E) = ∫[Eg to 2Eg] [1/cosh((E-E')/Gamma)] × f(E') dE'
```

여기서:
```
f(E') = (1 + b)/(1 - exp(-2π√(Eb/(E'-Eg))))
b = 10×mhcnp×(E'-Eg) + 126×mhcnp²×(E'-Eg)²
```

### 3.3 최종 흡수 계수

```
α(E) = ucvsq × √Eb × [a_exciton(E) + a_band(E)]
```

### 3.4 최적화 목적 함수

```
SSE = Σ [α_fitted(Ei) - α_measured(Ei)]²
```

L-BFGS-B 알고리즘으로 SSE를 최소화하는 파라미터를 찾습니다.

## 4. 사용 예시

### 4.1 기본 사용법

```python
from fitter import FSumFitter

# Fitter 생성
fitter = FSumFitter(deltaE=0.2, NS=20, fitmode=2)

# 파일 분석
results = fitter.process_file('data.txt', baseline_select=True)

# 결과 저장
fitter.save_results(results, output_dir='.')

# 그래프 생성
fitter.plot_results(results, save_path='results.pdf')
```

### 4.2 파라미터 커스터마이징

```python
fitter = FSumFitter()

# 초기값 설정
fitter.start_point = np.array([2.60, 0.055, 0.040, 35, 0.065, 0.2])

# 경계값 설정
fitter.lb = np.array([2.50, 0.01, 0.00, 0.010, 0.000, 0.0])
fitter.rb = np.array([2.70, 0.25, 0.25, 1000.0, 0.999, 1.5])

results = fitter.process_file('data.txt')
```

### 4.3 시뮬레이션 사용

```bash
python3 simulation/simulation.py
```

대화형으로 파라미터를 입력받아 이론 스펙트럼을 생성합니다.

## 5. 출력 파일 형식

### 5.1 CSV 결과 파일 (`*_Results.csv`)

각 데이터셋에 대해:
- **헤더**: 파라미터 설명
- **파라미터 값**: Eg, Eb_Rydberg, Eb_GroundState, Gamma, ucvsq, mhcnp, q, Deff, R²
- **데이터**: Wavelength, Raw Data, Baseline, Fitted Exciton, Fitted Band, Fitted Result

### 5.2 PDF 그래프 (`*.pdf`)

- Raw data (검은색 점)
- Baseline (회색 점선)
- Fitted Exciton (파란색 실선)
- Fitted Band (빨간색 실선)
- Fitted Result Total (초록색 굵은 실선)
- Fitting range 표시 (초록색 수직선)
- Baseline range 표시 (주황색 수직선)

## 6. 물리적 해석 가이드

### 6.1 q 값 해석

- **q ≈ 0**: Bulk 반도체 특성, 3D exciton
- **q ≈ 0.5-0.6**: Quasi-2D 구조 (양자우물, 2D 반도체)
- **q > 1**: 강한 양자 구속 (양자점, 나노입자)

### 6.2 Eb 해석

- **Eb (Rydberg)**: 코드에서 직접 피팅되는 파라미터
- **Eb (Ground State)**: 실제 n=1 exciton binding energy
  ```
  Eb_GS = Eb_Rydberg / (1-q)²
  ```
- q가 클수록 (구속이 강할수록) Eb_GS가 증가

### 6.3 Gamma 해석

- **작은 Gamma**: 날카로운 피크, 높은 결정성
- **큰 Gamma**: 넓은 피크, 불순물/온도 효과, 비결정성

### 6.4 R² 값

- **R² > 0.99**: 매우 좋은 피팅
- **R² > 0.95**: 좋은 피팅
- **R² < 0.90**: 피팅 개선 필요 (baseline 선택, 범위 조정 등)

## 7. 주의사항 및 팁

### 7.1 Baseline 선택

- **중요**: Baseline 선택이 피팅 품질에 큰 영향을 미칩니다
- 투명 구간(흡수가 거의 없는 에너지 범위)을 선택하세요
- fitmode=2 (Rayleigh scattering)는 나노입자 산란을 고려합니다

### 7.2 피팅 범위

- Bandgap 주변 (Eg ± 0.5 eV)에 집중하는 것이 좋습니다
- 너무 넓은 범위는 고에너지 영역의 오차를 증가시킬 수 있습니다
- `auto_range=True` (기본값)로 자동 최적화 가능

### 7.3 초기값 설정

- Eg는 데이터에서 자동 탐지되지만, 사용자가 제공한 값이 범위 내에 있으면 우선 사용됩니다
- Eb, Gamma는 실험 조건(온도, 샘플 품질)에 따라 달라질 수 있습니다
- q는 샘플 구조에 따라 설정하세요 (bulk=0, 2D=0.5-0.6, QD=1.5)


### 7.4 다중 데이터셋

- 한 파일에 여러 데이터셋(예: 온도 변화, 시간 변화)을 포함할 수 있습니다
- `T=[1,2,3]` 옵션으로 특정 데이터셋만 분석 가능
- 각 데이터셋은 독립적으로 피팅됩니다

## 8. 참고 문헌 및 이론적 배경

### 주요 참고 문헌

1. **Elliot, R. J. (1957)**: "Intensity of Optical Absorption by Excitons", Physical Review, 108, 1384-1389
   - 원본 Elliot Theory 제안

2. **F-sum Rule**: 전기 쌍극자 전이의 oscillator strength 합 규칙
   - Thomas-Reiche-Kuhn sum rule
   - Bethe sum rule

3. **Fractional Dimension Model**: 
   - 나노구조에서의 양자 구속 효과
   - Effective dimension 개념

### 관련 이론

- **Wannier-Mott Exciton**: 약하게 결합된 exciton 모델
- **Quantum Confinement**: 나노구조에서의 양자 구속 효과
- **Urbach Tail**: 밴드갭 아래의 지수적 흡수 꼬리
- **Rayleigh Scattering**: 나노입자에 의한 E⁴ 산란

## 9. 코드 개선 및 확장 가능성

### 현재 구현된 기능

- ✅ F-sum rule 기반 피팅
- ✅ Exciton/Band 분리
- ✅ 다중 데이터셋 처리
- ✅ Baseline 자동/수동 선택
- ✅ Urbach energy 분석
- ✅ 시뮬레이션 기능

### 가능한 확장

- 온도 의존성 분석
- 시간 분해 스펙트럼 분석
- 다중 exciton 분석
- 자동 파라미터 탐색 및 최적화
- 웹 인터페이스 (일부 구현됨)

## 10. 결론

이 코드는 Elliot Theory를 기반으로 반도체 및 나노구조 물질의 광학 흡수 스펙트럼을 정량적으로 분석하는 강력한 도구입니다. Exciton과 band-to-band 전이를 분리하여 분석함으로써, 물질의 전자 구조와 양자 구속 효과를 이해할 수 있습니다.

**핵심 가치**:
- 과학적으로 엄밀한 이론 기반 분석
- 정량적 파라미터 추출
- 다양한 나노구조 물질에 적용 가능
- 사용자 친화적인 인터페이스

이 도구를 통해 실험 데이터에서 물리적 의미를 가진 파라미터들을 정확하게 추출하고, 샘플의 구조적 특성과 전자적 특성을 이해할 수 있습니다.

