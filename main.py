"""
Command-line interface for F-sum rule fitting
Python implementation of main.m
"""
import argparse
import numpy as np
from api.fitter import FSumFitter

def _prompt_fitmode(default=2):
    print()
    print("fitmode를 선택하세요:")
    print("  0 = No baseline")
    print("  1 = Linear baseline")
    print("  2 = Rayleigh scattering baseline (E^4)")
    while True:
        s = input(f"fitmode 입력 (0/1/2) [기본값: {default}]: ").strip()
        if s == "":
            return default
        if s in ("0", "1", "2"):
            return int(s)
        print("❌ 잘못된 입력입니다. 0, 1, 2 중 하나를 입력하세요.")


def main():
    parser = argparse.ArgumentParser(
        description='F-sum rule fitting tool (Python version of main.m)'
    )
    parser.add_argument('filename', type=str, help='Input data file path')
    parser.add_argument('--deltaE', type=float, default=0.2,
                       help='Offset of normalization energy (default: 0.2)')
    parser.add_argument('--NS', type=int, default=20,
                       help='Number of datapoints for baseline interpolation (default: 20)')
    parser.add_argument('--fitmode', type=int, default=2,
                       choices=[0, 1, 2],
                       help='Baseline fit mode: 0=no fit, 1=linear, 2=power function (default: 2)')
    parser.add_argument('--choose-fitmode', action='store_true',
                       help='Choose fitmode interactively at runtime (overrides --fitmode)')
    parser.add_argument('--datasets', type=str, default=None,
                       help='Comma-separated list of dataset indices to fit (1-indexed, default: all)')
    parser.add_argument('--no-plot', action='store_true',
                       help='Do not display plots')
    # Baseline selection is required (automatic baseline is removed).
    # Keep --baseline-select for backwards compatibility; default is True.
    parser.add_argument('--baseline-select', action='store_true', dest='baseline_select',
                       help='(default) Interactively select Step 0 baseline range from a plot (click two points)')
    parser.add_argument('--no-baseline-select', action='store_false', dest='baseline_select',
                       help='Disable baseline selection (will error because auto baseline is removed)')
    parser.set_defaults(baseline_select=True)
    parser.add_argument('--output-dir', type=str, default='.',
                       help='Output directory for results (default: current directory)')
    
    args = parser.parse_args()
    
    # Parse dataset list
    T = None
    if args.datasets:
        T = [int(x.strip()) for x in args.datasets.split(',')]
    
    fitmode = args.fitmode
    if args.choose_fitmode:
        fitmode = _prompt_fitmode(default=fitmode)

    # Initialize fitter
    fitter = FSumFitter(deltaE=args.deltaE, NS=args.NS, fitmode=fitmode)
    
    # Process file
    print(f"Processing file: {args.filename}")
    results = fitter.process_file(args.filename, T=T, baseline_select=args.baseline_select)
    
    # Save results
    print(f"\nSaving results to {args.output_dir}")
    fitter.save_results(results, output_dir=args.output_dir)
    
    # Plot results
    if not args.no_plot:
        name_with_prefix = f"0_{results['name']}"
        save_path = f"{args.output_dir}/{name_with_prefix}.pdf"
        print(f"Generating plot: {save_path}")
        fitter.plot_results(results, save_path=save_path)
    
    print("\nDone!")


if __name__ == '__main__':
    main()
