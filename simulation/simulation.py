"""
시뮬레이션 프로그램
피팅 파라미터를 입력받아 해당하는 그래프를 생성합니다.
"""
import os
import sys
import tempfile
import numpy as np

# 상위 디렉토리의 모듈 import를 위해 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fsum2d import fsum2d

# Ensure Matplotlib has a writable config/cache directory
_mpl_config_dir = os.path.join(tempfile.gettempdir(), "matplotlib")
try:
    os.makedirs(_mpl_config_dir, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", _mpl_config_dir)
except Exception:
    pass

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정 (macOS)
try:
    font_list = [f.name for f in fm.fontManager.ttflist]
    korean_fonts = ['AppleGothic', 'NanumGothic', 'NanumBarunGothic', 'Malgun Gothic', 'Apple SD Gothic Neo']
    korean_font = None
    for font_name in korean_fonts:
        if font_name in font_list:
            korean_font = font_name
            break
    
    if korean_font:
        plt.rcParams['font.family'] = korean_font
        plt.rcParams['axes.unicode_minus'] = False
except Exception:
    pass


def get_parameter_input():
    """
    사용자로부터 파라미터 값을 입력받습니다.
    
    Returns:
    --------
    params : array
        [Eg, Eb, Gamma, ucvsq, mhcnp, q]
    """
    print("=" * 60)
    print("피팅 파라미터 입력")
    print("=" * 60)
    print()
    
    # 기본값 표시
    print("기본값을 사용하려면 Enter를 누르세요.")
    print()
    
    try:
        # Eg: Band gap energy (eV)
        eg_input = input("Eg (Band gap energy, eV) [기본값: 2.62]: ").strip()
        Eg = float(eg_input) if eg_input else 2.62
        
        # Eb: Exciton binding energy (eV) - 입력은 meV로 받고 eV로 변환
        eb_input = input("Eb (Exciton binding energy, meV) [기본값: 50]: ").strip()
        Eb_meV = float(eb_input) if eb_input else 50.0
        Eb = Eb_meV / 1000.0  # meV를 eV로 변환
        
        # Gamma: Linewidth (eV) - 입력은 meV로 받고 eV로 변환
        gamma_input = input("Gamma (Linewidth, meV) [기본값: 100]: ").strip()
        Gamma_meV = float(gamma_input) if gamma_input else 100.0
        Gamma = Gamma_meV / 1000.0  # meV를 eV로 변환
        
        # ucvsq: Transition dipole moment squared
        ucvsq_input = input("ucvsq (Transition dipole moment squared) [기본값: 10]: ").strip()
        ucvsq = float(ucvsq_input) if ucvsq_input else 10.0
        
        # mhcnp: Mass parameter
        mhcnp_input = input("mhcnp (Mass parameter) [기본값: 0.060]: ").strip()
        mhcnp = float(mhcnp_input) if mhcnp_input else 0.060
        
        # q: Fractional dimension parameter
        q_input = input("q (Fractional dimension, 0=bulk, 0.5-0.6=quasi-2D, 1.5=strong QD) [기본값: 0.2]: ").strip()
        q = float(q_input) if q_input else 0.2
        
        params = np.array([Eg, Eb, Gamma, ucvsq, mhcnp, q])
        
        print()
        print("=" * 60)
        print("입력된 파라미터:")
        print(f"  Eg = {Eg:.4f} eV")
        print(f"  Eb = {Eb*1000:.2f} meV (Rydberg)")
        print(f"  Gamma = {Gamma*1000:.2f} meV")
        print(f"  ucvsq = {ucvsq:.4f}")
        print(f"  mhcnp = {mhcnp:.4f}")
        print(f"  q = {q:.4f}")
        print(f"  Deff = {3 - 2*q:.4f}")
        
        # 실제 Ground State Binding Energy 계산
        if abs(1.0 - q) > 1e-5:
            eb_actual = Eb / ((1.0 - q)**2)
            print(f"  Eb(Ground State) = {eb_actual*1000:.2f} meV")
        else:
            print(f"  Eb(Ground State) = {Eb*1000:.2f} meV")
        print("=" * 60)
        print()
        
        return params
        
    except ValueError as e:
        print(f"❌ 오류: 잘못된 입력입니다. 숫자를 입력해주세요. ({e})")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n프로그램이 취소되었습니다.")
        sys.exit(0)


def get_energy_range_input(Eg):
    """
    에너지 범위를 입력받습니다.
    
    Parameters:
    -----------
    Eg : float
        Band gap energy (eV)
    
    Returns:
    --------
    energy_min : float
        최소 에너지 (eV)
    energy_max : float
        최대 에너지 (eV)
    """
    print("에너지 범위 설정 (eV 단위)")
    print(f"권장 범위: {Eg - 0.8:.2f} ~ {Eg + 0.8:.2f} eV")
    print()
    
    try:
        min_input = input(f"최소 에너지 (eV) [기본값: {Eg - 0.8:.2f}]: ").strip()
        energy_min = float(min_input) if min_input else Eg - 0.8
        
        max_input = input(f"최대 에너지 (eV) [기본값: {Eg + 0.8:.2f}]: ").strip()
        energy_max = float(max_input) if max_input else Eg + 0.8
        
        if energy_min >= energy_max:
            print("⚠️  경고: 최소 에너지가 최대 에너지보다 크거나 같습니다. 기본값을 사용합니다.")
            energy_min = Eg - 0.8
            energy_max = Eg + 0.8
        
        return energy_min, energy_max
        
    except ValueError:
        print("⚠️  경고: 잘못된 입력입니다. 기본값을 사용합니다.")
        return Eg - 0.8, Eg + 0.8


def simulate_spectrum(params, energy_min, energy_max, num_points=1000):
    """
    주어진 파라미터로 스펙트럼을 시뮬레이션합니다.
    
    Parameters:
    -----------
    params : array
        [Eg, Eb, Gamma, ucvsq, mhcnp, q]
    energy_min : float
        최소 에너지 (eV)
    energy_max : float
        최대 에너지 (eV)
    num_points : int
        데이터 포인트 개수
    
    Returns:
    --------
    energy : array
        에너지 데이터 (eV)
    wavelength : array
        파장 데이터 (nm)
    fitted_curve : array
        전체 피팅 곡선
    exciton : array
        Exciton 기여
    band : array
        Band 기여
    """
    # 에너지 범위 생성
    energy = np.linspace(energy_min, energy_max, num_points)
    
    # 더미 ydata (실제로는 사용되지 않지만 fsum2d 함수에 필요)
    ydata = np.zeros_like(energy)
    
    # fsum2d 함수 호출
    _, fitted_curve, exciton, band = fsum2d(params, energy, ydata)
    
    # 에너지를 파장으로 변환: λ(nm) = 1239.84193 / E(eV)
    wavelength = 1239.84193 / energy
    
    return energy, wavelength, fitted_curve, exciton, band


def plot_simulation(energy, wavelength, fitted_curve, exciton, band, params, save_path=None):
    """
    시뮬레이션 결과를 그래프로 그립니다.
    
    Parameters:
    -----------
    energy : array
        에너지 데이터 (eV)
    wavelength : array
        파장 데이터 (nm)
    fitted_curve : array
        전체 피팅 곡선
    exciton : array
        Exciton 기여
    band : array
        Band 기여
    params : array
        파라미터 [Eg, Eb, Gamma, ucvsq, mhcnp, q]
    save_path : str, optional
        저장 경로
    """
    Eg, Eb, Gamma, ucvsq, mhcnp, q = params
    
    # 실제 Ground State Binding Energy 계산
    if abs(1.0 - q) > 1e-5:
        eb_actual = Eb / ((1.0 - q)**2)
    else:
        eb_actual = Eb
    
    # 두 개의 subplot 생성: 에너지 vs 파장
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 왼쪽: 에너지 (eV) 기준
    ax1.plot(energy, fitted_curve, '-', color='green', linewidth=2.5, label='Total (Exciton + Band)')
    ax1.plot(energy, exciton, '-', color='blue', linewidth=2, label='Exciton')
    ax1.plot(energy, band, '-', color='red', linewidth=2, label='Band')
    
    # Band gap 표시
    ax1.axvline(x=Eg, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label=f'Eg = {Eg:.3f} eV')
    
    ax1.set_xlabel('Energy (eV)', fontsize=12)
    ax1.set_ylabel('Absorption', fontsize=12)
    ax1.set_title('Simulation: Energy vs Absorption', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10, loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([-0.1, np.max(fitted_curve) * 1.1])
    
    # 오른쪽: 파장 (nm) 기준 (역순으로 표시)
    # 파장은 내림차순으로 정렬 (높은 에너지 = 짧은 파장이 왼쪽)
    sort_idx = np.argsort(wavelength)[::-1]  # 내림차순 정렬 인덱스
    wavelength_sorted = wavelength[sort_idx]
    fitted_curve_sorted = fitted_curve[sort_idx]
    exciton_sorted = exciton[sort_idx]
    band_sorted = band[sort_idx]
    
    ax2.plot(wavelength_sorted, fitted_curve_sorted, '-', color='green', linewidth=2.5, label='Total (Exciton + Band)')
    ax2.plot(wavelength_sorted, exciton_sorted, '-', color='blue', linewidth=2, label='Exciton')
    ax2.plot(wavelength_sorted, band_sorted, '-', color='red', linewidth=2, label='Band')
    
    # Band gap에 해당하는 파장 표시
    wavelength_eg = 1239.84193 / Eg
    ax2.axvline(x=wavelength_eg, color='black', linestyle='--', linewidth=1.5, alpha=0.7, 
                label=f'Eg = {wavelength_eg:.1f} nm')
    
    ax2.set_xlabel('Wavelength (nm)', fontsize=12)
    ax2.set_ylabel('Absorption', fontsize=12)
    ax2.set_title('Simulation: Wavelength vs Absorption', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10, loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([-0.1, np.max(fitted_curve) * 1.1])
    
    # 전체 제목에 파라미터 정보 추가
    title_text = (f'Eg={Eg:.3f} eV, Eb(GS)={eb_actual*1000:.1f} meV, '
                  f'Gamma={Gamma*1000:.1f} meV, q={q:.3f}, Deff={3-2*q:.3f}')
    fig.suptitle(title_text, fontsize=11, y=0.98)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, format='pdf', dpi=300, bbox_inches='tight')
        print(f"✅ 그래프가 저장되었습니다: {save_path}")
    else:
        plt.show()
    
    return fig


def save_simulation_data(energy, wavelength, fitted_curve, exciton, band, params, output_path):
    """
    시뮬레이션 데이터를 CSV 파일로 저장합니다.
    
    Parameters:
    -----------
    energy : array
        에너지 데이터 (eV)
    wavelength : array
        파장 데이터 (nm)
    fitted_curve : array
        전체 피팅 곡선
    exciton : array
        Exciton 기여
    band : array
        Band 기여
    params : array
        파라미터
    output_path : str
        출력 파일 경로
    """
    import csv
    
    Eg, Eb, Gamma, ucvsq, mhcnp, q = params
    
    # 실제 Ground State Binding Energy 계산
    if abs(1.0 - q) > 1e-5:
        eb_actual = Eb / ((1.0 - q)**2)
    else:
        eb_actual = Eb
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # 헤더
        writer.writerow(['Simulation Parameters'])
        writer.writerow([])
        writer.writerow(['Parameter', 'Value', 'Unit', 'Description'])
        writer.writerow(['Eg', f'{Eg:.6f}', 'eV', 'Band gap energy'])
        writer.writerow(['Eb_Rydberg', f'{Eb*1000:.6f}', 'meV', 'Effective Rydberg constant'])
        writer.writerow(['Eb_GroundState', f'{eb_actual*1000:.6f}', 'meV', 'Actual Ground State Binding Energy'])
        writer.writerow(['Gamma', f'{Gamma*1000:.6f}', 'meV', 'Linewidth (broadening)'])
        writer.writerow(['ucvsq', f'{ucvsq:.6f}', '', 'Transition dipole moment squared'])
        writer.writerow(['mhcnp', f'{mhcnp:.6f}', '', 'Mass parameter'])
        writer.writerow(['q', f'{q:.6f}', '', 'Fractional dimension parameter'])
        writer.writerow(['Deff', f'{3-2*q:.6f}', '', 'Effective dimension'])
        writer.writerow([])
        writer.writerow([])
        
        # 데이터 헤더
        writer.writerow(['Wavelength (nm)', 'Energy (eV)', 'Total Absorption', 'Exciton', 'Band'])
        
        # 데이터 (파장 내림차순으로 정렬)
        sort_idx = np.argsort(wavelength)[::-1]
        for i in sort_idx:
            writer.writerow([
                f'{wavelength[i]:.6f}',
                f'{energy[i]:.6f}',
                f'{fitted_curve[i]:.6f}',
                f'{exciton[i]:.6f}',
                f'{band[i]:.6f}'
            ])
    
    print(f"✅ 데이터가 저장되었습니다: {output_path}")


def main():
    """
    메인 함수
    """
    print()
    print("=" * 60)
    print("Elliot Fitting 시뮬레이션 프로그램")
    print("=" * 60)
    print()
    
    # 파라미터 입력
    params = get_parameter_input()
    Eg = params[0]
    
    # 에너지 범위 입력
    energy_min, energy_max = get_energy_range_input(Eg)
    
    print()
    print("시뮬레이션을 실행합니다...")
    print(f"에너지 범위: {energy_min:.3f} ~ {energy_max:.3f} eV")
    print()
    
    # 시뮬레이션 실행
    energy, wavelength, fitted_curve, exciton, band = simulate_spectrum(
        params, energy_min, energy_max, num_points=1000
    )
    
    # 그래프 그리기
    print("그래프를 생성합니다...")
    fig = plot_simulation(energy, wavelength, fitted_curve, exciton, band, params)
    
    # 저장 여부 확인
    save_choice = input("\n결과를 저장하시겠습니까? (y/n) [기본값: n]: ").strip().lower()
    
    if save_choice == 'y' or save_choice == 'yes':
        # 현재 디렉토리
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 그래프 저장
        graph_path = os.path.join(current_dir, 'simulation_result.pdf')
        fig.savefig(graph_path, format='pdf', dpi=300, bbox_inches='tight')
        print(f"✅ 그래프가 저장되었습니다: {graph_path}")
        
        # 데이터 저장
        data_path = os.path.join(current_dir, 'simulation_result.csv')
        save_simulation_data(energy, wavelength, fitted_curve, exciton, band, params, data_path)
    
    print()
    print("=" * 60)
    print("시뮬레이션이 완료되었습니다!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램이 취소되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
