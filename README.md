# Elliot Fitting: Exciton Binding Energy Analysis

Absorption spectrum으로부터 f-sum rule과 Elliot theory를 사용하여 exciton binding energy를 계산하는 Python 패키지입니다.

## 기능

- **Elliot Theory 기반 피팅**: Absorption spectrum을 exciton과 band-to-band 전이로 분리
- **Exciton Binding Energy 계산**: 최적화를 통해 Eb 값을 추출
- **Baseline Subtraction**: 다양한 방법으로 baseline 제거
- **Urbach Energy 추출**: 밴드갭 근처의 Urbach tail 분석
- **시각화**: 피팅 결과와 exciton/band 성분을 그래프로 표시

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

### 기본 사용

```python
from elliot_fitting import fit_absorption_spectrum

# 데이터 파일 로드 및 피팅
results = fit_absorption_spectrum('data.txt')
```

### 고급 사용

```python
from elliot_fitting import ElliotFitter

fitter = ElliotFitter(
    start_point=[2.62, 0.050, 0.043, 37, 0.060, 0],
    bounds=([2.54, 0.01, 0.00, 0.010, 0.000, 0],
            [2.68, 0.2, 0.20, 1000.0, 0.999, 0]),
    fitmode=2,
    NS=20
)

results = fitter.fit('data.txt')
fitter.plot_results()
fitter.save_results('output')
```

## 파라미터 설명

피팅 파라미터 (6개):
- **Eg**: Band gap energy (eV)
- **Eb**: Exciton binding energy (eV) - 목표값
- **Gamma**: 선폭 (eV)
- **ucvsq**: 전이 쌍극자 모멘트 제곱
- **mhcnp**: 비율 파라미터
- **q**: 차원 파라미터 (0: bulk, 0.5~0.6: quasi-2D, 1.5: QD)

## 입력 데이터 형식

텍스트 파일 형식:
```
Energy(eV)  Absorption1  Absorption2  ...
2.50        0.001       0.002        ...
2.51        0.0015      0.0025       ...
...
```

첫 번째 열은 에너지, 이후 열들은 각각의 absorption 데이터입니다.

## 출력 파일

- `*_FittedBand.dat`: Band-to-band 전이 성분
- `*_FittedExciton.dat`: Exciton 전이 성분
- `*_FitResult.dat`: 피팅 결과 (파라미터, R², Urbach energy 등)
- `*.pdf`: 피팅 결과 그래프

## 참고문헌

- Elliot theory 기반 absorption spectrum 분석
- f-sum rule을 사용한 exciton binding energy 계산

## 라이선스

MIT License

## 기여

이슈와 풀 리퀘스트를 환영합니다!

## 저장소

GitHub: [https://github.com/jinwoo7park/Eliot-model](https://github.com/jinwoo7park/Eliot-model)

