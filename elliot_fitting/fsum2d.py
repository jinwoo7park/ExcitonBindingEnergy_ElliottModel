"""
fsum2D: Elliot theory 기반 absorption spectrum 계산 함수

이 함수는 Elliot theory를 사용하여 주어진 파라미터에 대해
exciton과 band-to-band 전이를 계산합니다.
"""

import numpy as np


def fsum2d(params, xdata, ydata):
    """
    Elliot theory 기반 absorption spectrum 계산
    
    Parameters
    ----------
    params : array-like
        [Eg, Eb, Gamma, ucvsq, mhcnp, q]
        - Eg: Band gap energy (eV)
        - Eb: Exciton binding energy (eV)
        - Gamma: 선폭 (eV)
        - ucvsq: 전이 쌍극자 모멘트 제곱
        - mhcnp: 비율 파라미터
        - q: 차원 파라미터 (0: bulk, 0.5~0.6: quasi-2D, 1.5: QD)
    xdata : array-like
        에너지 데이터 (eV)
    ydata : array-like
        실험 absorption 데이터
        
    Returns
    -------
    sse : float
        Sum of squared errors
    FittedCurve : array
        전체 피팅 곡선 (exciton + band)
    exciton : array
        Exciton 전이 성분
    band : array
        Band-to-band 전이 성분
    """
    Eg = params[0]
    Eb = params[1]
    gamma = params[2]
    ucvsq = params[3]
    mhcnp = params[4]
    q = params[5]
    
    xdata = np.array(xdata)
    ydata = np.array(ydata)
    
    # Exciton 전이 계산 (최대 50개 level)
    a1 = np.zeros(len(xdata))
    for i in range(1, 51):
        Enx = Eg - (Eb / (i - q)**2)
        anx = 2 * Eb / (i - q)**3 * np.sech((xdata - Enx) / gamma)
        a1 = a1 + anx
    
    # Band-to-band 전이 계산
    E = np.linspace(Eg, 2 * Eg, 10 * len(xdata))
    a2 = np.zeros((len(E), len(xdata)))
    
    for i in range(len(E)):
        b = 10 * mhcnp * (E[i] - Eg) + 126 * mhcnp**2 * (E[i] - Eg)**2
        a2[i, :] = np.sech((xdata - E[i]) / gamma) * (
            (1 + b) / (1 - np.exp(-2 * np.pi * np.sqrt(Eb / (E[i] - Eg))))
        )
    
    # 적분 계산 (trapz는 마지막 축을 따라 적분)
    band_integral = np.trapz(a2, E, axis=0)
    
    # 전체 곡선 계산
    FittedCurve = ucvsq * np.sqrt(Eb) * (band_integral + a1)
    exciton = ucvsq * np.sqrt(Eb) * a1
    band = ucvsq * np.sqrt(Eb) * band_integral
    
    # SSE 계산
    ErrorVector = FittedCurve - ydata
    sse = np.sum(ErrorVector**2)
    
    # mhcnp가 음수이면 penalty 부여
    if mhcnp <= 0:
        sse = 10 * sse
    
    return sse, FittedCurve, exciton, band


def fsum2d_wrapper_factory(xdata, ydata):
    """
    최적화를 위한 wrapper 함수 팩토리
    
    Parameters
    ----------
    xdata : array-like
        에너지 데이터
    ydata : array-like
        실험 absorption 데이터
        
    Returns
    -------
    wrapper : function
        최적화에 사용할 wrapper 함수
    """
    def wrapper(params):
        sse, _, _, _ = fsum2d(params, xdata, ydata)
        return sse
    return wrapper

