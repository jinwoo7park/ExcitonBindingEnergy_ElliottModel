"""
FastAPI 백엔드 서버
ExcitonBindingEnergy_ElliottModel - Exciton binding energy calculation using Elliott Model
"""
import sys
import os

# Add current directory to sys.path to ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import tempfile
import numpy as np
import base64
from io import BytesIO, StringIO
import traceback

# Import from local module
from .fitter import FSumFitter

app = FastAPI(title="ExcitonBindingEnergy_ElliottModel API")

# CORS 설정
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,https://elliott-model.vercel.app"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 임시 파일 저장 디렉토리 (Vercel 환경에서는 /tmp만 쓰기 가능)
TEMP_DIR = tempfile.mkdtemp(prefix="fsum_fitting_")

class InitialValues(BaseModel):
    Eg: float = 2.62  # eV
    Eb: float = 50.0  # meV
    Gamma: float = 100.0  # meV
    ucvsq: float = 10
    mhcnp: float = 0.060
    q: float = 0.2

class Bounds(BaseModel):
    Eg: Optional[dict] = None
    Eb: Optional[dict] = None
    Gamma: Optional[dict] = None
    ucvsq: Optional[dict] = None
    mhcnp: Optional[dict] = None
    q: Optional[dict] = None
    
    class Config:
        extra = "allow"

class AnalyzeRequest(BaseModel):
    filename: str = "data"
    xdata: List[float] # eV 단위
    ydata: List[float] # Absorption
    fitmode: int = 2
    baseline_points: List[float]
    initial_values: Optional[InitialValues] = None
    bounds: Optional[Bounds] = None

@app.get("/api")
@app.get("/")
async def root():
    return {"message": "ExcitonBindingEnergy_ElliottModel API", "version": "1.0.0"}

@app.post("/api/preview")
async def preview_file(file: UploadFile = File(...)):
    """
    파일을 업로드하고 데이터를 파싱하여 반환합니다.
    Stateless 처리를 위해 파싱된 데이터를 클라이언트로 돌려보냅니다.
    """
    try:
        # 파일 내용 읽기
        content = await file.read()
        
        # fitter를 사용하여 데이터 읽기 로직 재사용 (임시 파일 사용 없이 직접 처리하고 싶지만, 
        # fitter.process_file이 파일 경로를 요구하므로 임시 파일 생성 불가피)
        # 하지만 여기서는 단순 파싱이므로 직접 파싱 로직을 구현하는 게 나음
        
        # 메모리 상의 파일 내용을 텍스트로 디코딩
        encodings = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr', 'latin-1']
        text_content = None
        for encoding in encodings:
            try:
                text_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
                
        if text_content is None:
            raise ValueError("파일을 읽을 수 없습니다. 지원되지 않는 인코딩입니다.")
            
        # 데이터 파싱
        lines = text_content.splitlines()
        data_start_idx = 0
        delimiter = ',' if file.filename.lower().endswith('.csv') else None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if delimiter:
                parts = [p.strip() for p in line.split(delimiter)]
            else:
                parts = line.split()
            if len(parts) < 2:
                continue
            try:
                float(parts[0])
                float(parts[1])
                data_start_idx = i
                break
            except ValueError:
                continue
        
        data_lines = [lines[i].strip() for i in range(data_start_idx, len(lines)) if lines[i].strip()]
        data_string = '\n'.join(data_lines)
        
        if delimiter:
            raw = np.loadtxt(StringIO(data_string), delimiter=',')
        else:
            raw = np.loadtxt(StringIO(data_string))
            
        if len(raw.shape) == 1 or raw.shape[1] < 2:
            raise ValueError("데이터 형식이 올바르지 않습니다. 최소 2열이 필요합니다.")
            
        xdata_original = raw[:, 0]
        ydata = raw[:, 1]
        xdata = 1239.84193 / xdata_original # nm to eV
        
        # 미리보기 그래프 생성 (Matplotlib)
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(10, 6))
        margins = {'left': 0.12, 'right': 0.95, 'bottom': 0.12, 'top': 0.90}
        fig.subplots_adjust(**margins)
        
        ax.plot(xdata, ydata, '-', color='black', linewidth=1.5, alpha=0.7)
        ax.set_xlabel('Energy (eV)', fontsize=12)
        ax.set_ylabel('Absorption', fontsize=12)
        ax.set_title('Baseline 및 피팅 범위 선택', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        x_min, x_max = np.min(xdata), np.max(xdata)
        ax.set_xlim(x_min, x_max)
        y_min, y_max = np.min(ydata), np.max(ydata)
        y_margin = (y_max - y_min) * 0.05
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches=None, pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        
        return {
            "success": True,
            "image": f"data:image/png;base64,{image_base64}",
            "xdata": xdata.tolist(),
            "ydata": ydata.tolist(),
            "filename": file.filename,
            "xmin": float(x_min),
            "xmax": float(x_max),
            "ymin": float(y_min),
            "ymax": float(y_max)
        }
        
    except Exception as e:
        print(f"Preview error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_data(request: AnalyzeRequest):
    """
    클라이언트로부터 데이터를 직접 받아서 분석합니다.
    """
    try:
        fitter = FSumFitter(deltaE=0.2, NS=20, fitmode=request.fitmode)
        
        # Initial values 설정
        if request.initial_values:
            iv = request.initial_values
            fitter.start_point = np.array([
                iv.Eg,
                iv.Eb / 1000.0,
                iv.Gamma / 1000.0,
                iv.ucvsq,
                iv.mhcnp,
                iv.q
            ])
            
        # Bounds 설정
        if request.bounds:
            bounds_data = request.bounds
            param_order = ['Eg', 'Eb', 'Gamma', 'ucvsq', 'mhcnp', 'q']
            new_lb = fitter.lb.copy()
            new_rb = fitter.rb.copy()
            
            # Pydantic v1/v2 호환 처리
            bounds_dict = {}
            if hasattr(bounds_data, 'model_dump'):
                bounds_dict = bounds_data.model_dump()
            elif hasattr(bounds_data, 'dict'):
                bounds_dict = bounds_data.dict()
            else:
                bounds_dict = bounds_data.__dict__
                
            for idx, param in enumerate(param_order):
                if param == 'Eg': continue
                
                param_bounds = bounds_dict.get(param)
                if param_bounds and isinstance(param_bounds, dict):
                    lower = param_bounds.get('lower')
                    upper = param_bounds.get('upper')
                    is_meV = (param in ['Eb', 'Gamma'])
                    
                    if lower is not None:
                        val = float(lower)
                        new_lb[idx] = val / 1000.0 if is_meV else val
                    if upper is not None:
                        val = float(upper)
                        new_rb[idx] = val / 1000.0 if is_meV else val
            
            fitter.lb = new_lb
            fitter.rb = new_rb

        # 분석 실행 (fitter.py에 새로 추가할 메서드 사용)
        # process_data_with_points는 결과 dict를 반환함
        results = fitter.process_data_with_points(
            xdata=request.xdata,
            ydata=request.ydata,
            baseline_points=request.baseline_points,
            fitmode=request.fitmode,
            name=request.filename
        )
        
        # 결과 처리
        fit_params = results['fitresult'][0] if len(results['fitresult']) > 0 else [0]*6
        quality = results['quality'][0] if len(results['quality']) > 0 else 0.0
        
        Eg = float(fit_params[0])
        Eb = float(fit_params[1])
        Gamma = float(fit_params[2])
        q = float(fit_params[5])
        
        # 경고 확인
        boundary_warnings = []
        tolerance = 0.002
        
        # Eg bounds check
        initial_Eg = request.initial_values.Eg if request.initial_values else 2.62
        if abs(Eg - (initial_Eg - 0.4)) <= tolerance or abs(Eg - (initial_Eg + 0.4)) <= tolerance:
            boundary_warnings.append("Eg (Band gap)")
            
        # Eb bounds check
        if abs(Eb - 0.01) <= tolerance or abs(Eb - 2.0) <= tolerance:
            boundary_warnings.append("R* (Rydberg constant)")
            
        # Gamma bounds check
        if abs(Gamma - 0.0) <= tolerance or abs(Gamma - 0.2) <= tolerance:
            boundary_warnings.append("Gamma")
            
        q_warning = "q값이 0.4보다 큽니다." if q > 0.4 else None
        
        Eb_actual = Eb / ((1.0 - q)**2) if abs(1.0 - q) > 1e-5 else Eb
        
        # 결과 파일 생성 (메모리에서)
        # 1. CSV
        # save_results는 파일로 저장함. 내용을 캡처하거나 별도 로직 구현 필요.
        # fitter.save_results를 수정하는 대신, 여기서 직접 CSV 문자열을 생성하거나
        # 임시 파일에 저장 후 읽어서 리턴. Vercel /tmp는 쓰기 가능.
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            fitter.save_results(results, output_dir=tmpdirname)
            
            # CSV 읽기
            csv_filename = f"0_{results['name']}_Results.csv"
            csv_path = os.path.join(tmpdirname, csv_filename)
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
                
            # 그래프 이미지 생성
            plot_path = os.path.join(tmpdirname, f"0_{results['name']}.pdf") # PDF로 저장됨
            # 웹 표시용으로 PNG도 필요하거나, PDF를 다운로드용으로 줌.
            # 하지만 미리보기용 이미지를 리턴해주면 좋음.
            
            # plot_results 메서드가 figure를 리턴하므로 이를 이용해서 PNG 생성
            fig = fitter.plot_results(results, save_path=None) # 화면 표시 모드지만 figure 리턴
            
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
            
            # PDF 파일 내용도 Base64로 인코딩하여 전달 (다운로드용)
            # plot_results가 save_path가 있으면 저장함.
            fitter.plot_results(results, save_path=plot_path)
            with open(plot_path, 'rb') as f:
                pdf_base64 = base64.b64encode(f.read()).decode('utf-8')

        return {
            "success": True,
            "name": results['name'],
            "parameters": {
                "Eg": Eg,
                "Eb_Rydberg": Eb * 1000.0,
                "Eb_GroundState": Eb_actual * 1000.0,
                "Gamma": Gamma * 1000.0,
                "ucvsq": float(fit_params[3]),
                "mhcnp": float(fit_params[4]),
                "q": q,
            },
            "quality": float(quality),
            "boundary_warnings": boundary_warnings,
            "q_warning": q_warning,
            "csv_content": csv_content,      # CSV 파일 텍스트 내용
            "plot_image": f"data:image/png;base64,{plot_base64}", # 결과 그래프 이미지
            "pdf_content": f"data:application/pdf;base64,{pdf_base64}" # PDF 다운로드용
        }
        
    except Exception as e:
        print(f"Analyze error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "mode": "serverless"}

# Local development support
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
