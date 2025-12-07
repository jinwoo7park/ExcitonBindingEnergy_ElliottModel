"""
ElliotFitter: Absorption spectrum 피팅을 위한 메인 클래스
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.optimize import curve_fit
from .fsum2d import fsum2d, fsum2d_wrapper_factory


class ElliotFitter:
    """
    Elliot theory 기반 absorption spectrum 피팅 클래스
    """
    
    def __init__(self, start_point=None, bounds=None, fitmode=2, NS=20, 
                 deltaE=0.2, T=None):
        """
        Parameters
        ----------
        start_point : array-like, optional
            초기 파라미터 값 [Eg, Eb, Gamma, ucvsq, mhcnp, q]
            기본값: [2.62, 0.050, 0.043, 37, 0.060, 0]
        bounds : tuple of arrays, optional
            파라미터 경계 [(lower_bounds), (upper_bounds)]
            기본값: ([2.54, 0.01, 0.00, 0.010, 0.000, 0],
                     [2.68, 0.2, 0.20, 1000.0, 0.999, 0])
        fitmode : int, optional
            Baseline 피팅 모드 (0: no fit, 1: linear, 2: power function)
            기본값: 2
        NS : int, optional
            Baseline 피팅에 사용할 데이터 포인트 수
            기본값: 20
        deltaE : float, optional
            정규화 에너지 오프셋
            기본값: 0.2
        T : array-like, optional
            피팅할 데이터셋 인덱스 리스트
            기본값: None (모든 데이터셋 피팅)
        """
        # 기본 파라미터 설정
        if start_point is None:
            self.start_point = np.array([2.62, 0.050, 0.043, 37, 0.060, 0])
        else:
            self.start_point = np.array(start_point)
            
        if bounds is None:
            self.bounds = ([2.54, 0.01, 0.00, 0.010, 0.000, 0],
                          [2.68, 0.2, 0.20, 1000.0, 0.999, 0])
        else:
            self.bounds = bounds
            
        self.fitmode = fitmode
        self.NS = NS
        self.deltaE = deltaE
        
        # 결과 저장용
        self.results = {}
        self.xdata = None
        self.raw_data = None
        
    def load_data(self, filename):
        """
        데이터 파일 로드
        
        Parameters
        ----------
        filename : str
            데이터 파일 경로
        """
        self.raw_data = np.loadtxt(filename)
        self.xdata = self.raw_data[:, 0]
        return self.raw_data
    
    def fit_baseline(self, energy, absorption):
        """
        Baseline 피팅
        
        Parameters
        ----------
        energy : array-like
            에너지 데이터
        absorption : array-like
            Absorption 데이터
            
        Returns
        -------
        baseline : array
            피팅된 baseline
        """
        # 마지막 NS개 포인트 사용
        energy_baseline = energy[-self.NS:][::-1]
        abs_baseline = absorption[-self.NS:][::-1]
        
        if self.fitmode == 0:
            # No baseline
            return np.zeros_like(energy)
        elif self.fitmode == 1:
            # Linear fit
            coeffs = np.polyfit(energy_baseline, abs_baseline, 1)
            baseline = np.polyval(coeffs, energy)
            return baseline
        elif self.fitmode == 2:
            # Power function fit: y = a * x^b
            # log(y) = log(a) + b*log(x)
            log_energy = np.log(energy_baseline[energy_baseline > 0])
            log_abs = np.log(abs_baseline[energy_baseline > 0])
            coeffs = np.polyfit(log_energy, log_abs, 1)
            a = np.exp(coeffs[1])
            b = coeffs[0]
            baseline = a * (energy**b)
            return baseline
        else:
            raise ValueError(f"fitmode {self.fitmode} not implemented")
    
    def fit_single_dataset(self, absorption, start_point=None):
        """
        단일 데이터셋 피팅
        
        Parameters
        ----------
        absorption : array-like
            Absorption 데이터
        start_point : array-like, optional
            초기 파라미터 값
            
        Returns
        -------
        result : dict
            피팅 결과 딕셔너리
        """
        if start_point is None:
            start_point = self.start_point.copy()
        
        # Baseline 제거
        baseline = self.fit_baseline(self.xdata, absorption)
        ydata = absorption - baseline
        
        # Wrapper 함수 생성
        wrapper = fsum2d_wrapper_factory(self.xdata, ydata)
        
        # 최적화
        result_opt = minimize(
            wrapper,
            start_point,
            method='L-BFGS-B',
            bounds=list(zip(self.bounds[0], self.bounds[1])),
            options={'maxiter': 1000, 'ftol': 1e-13}
        )
        
        estimates = result_opt.x
        
        # 피팅 곡선 계산
        sse, FittedCurve, exciton, band = fsum2d(estimates, self.xdata, ydata)
        
        # R² 계산
        ss_tot = np.sum((ydata - np.mean(ydata))**2)
        r_squared = 1 - sse / ss_tot
        
        # Urbach energy 계산
        # Eb - Eg 근처에서 linear fit
        threshold = np.abs(estimates[1] - estimates[0])
        indices = np.where(self.xdata < threshold)[0]
        if len(indices) > 10:
            idx_start = indices[-1] + 2
            idx_end = min(idx_start + 8, len(self.xdata))
            if idx_end > idx_start:
                x_urbach = self.xdata[idx_start:idx_end]
                y_urbach = np.log(ydata[idx_start:idx_end])
                valid = np.isfinite(y_urbach)
                if np.sum(valid) > 2:
                    coeffs = np.polyfit(x_urbach[valid], y_urbach[valid], 1)
                    slope = coeffs[0]
                    intersect = coeffs[1]
                else:
                    slope = np.nan
                    intersect = np.nan
            else:
                slope = np.nan
                intersect = np.nan
        else:
            slope = np.nan
            intersect = np.nan
        
        result = {
            'estimates': estimates,
            'sse': sse,
            'r_squared': r_squared,
            'FittedCurve': FittedCurve,
            'exciton': exciton,
            'band': band,
            'baseline': baseline,
            'cleandata': ydata,
            'slope': slope,
            'intersect': intersect,
            'urbach_energy': -1/slope if not np.isnan(slope) and slope < 0 else np.nan
        }
        
        return result
    
    def fit(self, filename, T=None):
        """
        데이터 파일을 로드하고 피팅 수행
        
        Parameters
        ----------
        filename : str
            데이터 파일 경로
        T : array-like, optional
            피팅할 데이터셋 인덱스 리스트 (1-based)
            None이면 모든 데이터셋 피팅
            
        Returns
        -------
        results : dict
            피팅 결과 딕셔너리
        """
        self.load_data(filename)
        
        if T is None:
            T = list(range(1, self.raw_data.shape[1]))
        else:
            T = np.array(T) - 1  # 0-based로 변환
        
        results = {}
        current_start = self.start_point.copy()
        
        for i in T:
            if i >= self.raw_data.shape[1] - 1:
                continue
            absorption = self.raw_data[:, i + 1]
            result = self.fit_single_dataset(absorption, current_start)
            results[i + 1] = result
            current_start = result['estimates'].copy()  # 다음 피팅의 초기값으로 사용
            
            print(f'Dataset {i+1}:')
            print(f'  Eg={result["estimates"][0]:.3f} eV, '
                  f'Eb={result["estimates"][1]:.3f} eV, '
                  f'Gamma={result["estimates"][2]:.3f} eV')
            print(f'  R²={result["r_squared"]:.4f}')
            print(f'  Effective dimension Deff={3-2*result["estimates"][5]:.3f}')
        
        self.results = results
        return results
    
    def plot_results(self, save_path=None):
        """
        피팅 결과 시각화
        
        Parameters
        ----------
        save_path : str, optional
            저장할 파일 경로 (PDF 형식)
        """
        if not self.results:
            raise ValueError("No results to plot. Run fit() first.")
        
        n_datasets = len(self.results)
        n_cols = int(np.ceil(np.sqrt(n_datasets)))
        n_rows = int(np.ceil(n_datasets / n_cols))
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 10))
        if n_datasets == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        
        for idx, (dataset_num, result) in enumerate(self.results.items()):
            ax = axes[idx]
            
            # 실험 데이터
            ax.plot(self.xdata, result['cleandata'], 'o', 
                   markersize=4, label='Experiment', alpha=0.6)
            
            # 피팅 곡선
            ax.plot(self.xdata, result['FittedCurve'], '-', 
                   linewidth=2, label='Fit', color='black')
            
            # Baseline 구분선
            baseline_idx = len(self.xdata) - self.NS
            ax.axvline(self.xdata[baseline_idx], '--', 
                      color='gray', alpha=0.5)
            
            # Band와 Exciton 성분
            ax.fill_between(self.xdata, 0, result['band'], 
                           alpha=0.5, color='red', label='Band')
            ax.fill_between(self.xdata, 0, result['exciton'], 
                           alpha=0.5, color='blue', label='Exciton')
            
            ax.set_xlabel('Energy (eV)')
            ax.set_ylabel('Absorption')
            ax.set_title(f'Dataset {dataset_num}: Eb={result["estimates"][1]:.3f} eV')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            ax.set_ylim([-0.1, np.max(result['FittedCurve']) * 1.1])
        
        # 빈 subplot 숨기기
        for idx in range(n_datasets, len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, format='pdf', dpi=300)
        else:
            plt.show()
    
    def save_results(self, output_prefix):
        """
        결과를 파일로 저장
        
        Parameters
        ----------
        output_prefix : str
            출력 파일 접두사
        """
        if not self.results:
            raise ValueError("No results to save. Run fit() first.")
        
        # 데이터 준비
        n_points = len(self.xdata)
        n_datasets = len(self.results)
        
        # Fitted curves
        fitted_curves = np.zeros((n_points, n_datasets + 1))
        fitted_curves[:, 0] = self.xdata
        
        fitted_exciton = np.zeros((n_points, n_datasets + 1))
        fitted_exciton[:, 0] = self.xdata
        
        fitted_band = np.zeros((n_points, n_datasets + 1))
        fitted_band[:, 0] = self.xdata
        
        # Fit results
        fit_results = []
        
        for idx, (dataset_num, result) in enumerate(self.results.items()):
            fitted_curves[:, idx + 1] = result['FittedCurve']
            fitted_exciton[:, idx + 1] = result['exciton']
            fitted_band[:, idx + 1] = result['band']
            
            fit_results.append([
                dataset_num,
                *result['estimates'],
                result['r_squared'],
                result['intersect'],
                result['slope']
            ])
        
        # 파일 저장
        np.savetxt(f'{output_prefix}_FittedBand.dat', fitted_band)
        np.savetxt(f'{output_prefix}_FittedExciton.dat', fitted_exciton)
        
        header = 'Dataset Eg Eb Gamma ucvsq mhcnp q R2 intersect slope'
        np.savetxt(f'{output_prefix}_FitResult.dat', fit_results, 
                  header=header, fmt='%d %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f')
        
        print(f"Results saved with prefix: {output_prefix}")

