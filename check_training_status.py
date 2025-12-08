"""
Check if training is still running without interrupting it.
This script checks if the training process is active.
"""

import os
import sys
from pathlib import Path

def check_training_status():
    """Check if training process is still running."""
    
    # Check if we're on Windows
    is_windows = os.name == 'nt'
    
    if is_windows:
        try:
            import psutil
            print("Checking for running Python training processes...")
            
            training_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline:
                        cmdline_str = ' '.join(cmdline).lower()
                        # Check if it's a training script
                        if 'train_from_csv' in cmdline_str or 'train_models' in cmdline_str:
                            training_processes.append({
                                'pid': proc.info['pid'],
                                'cpu': proc.info['cpu_percent'],
                                'memory_mb': proc.info['memory_info'].rss / 1024 / 1024,
                                'cmdline': ' '.join(cmdline)
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if training_processes:
                print(f"\n✅ Found {len(training_processes)} training process(es):")
                for proc in training_processes:
                    print(f"   PID: {proc['pid']}")
                    print(f"   CPU: {proc['cpu']:.1f}%")
                    print(f"   Memory: {proc['memory_mb']:.1f} MB")
                    print(f"   Command: {proc['cmdline'][:80]}...")
                    print()
                
                # Check if process is actively using CPU
                active = any(p['cpu'] > 0.1 for p in training_processes)
                if active:
                    print("🟢 Status: TRAINING IS ACTIVE (using CPU)")
                else:
                    print("🟡 Status: Process running but low CPU usage (may be loading/waiting)")
                
                return True
            else:
                print("❌ No training processes found")
                return False
                
        except ImportError:
            print("⚠️  psutil not installed. Installing basic status check...")
            print("\nTo check process status manually:")
            print("   Windows: Open Task Manager and look for Python processes")
            print("   Or run: tasklist | findstr python")
            return None
    else:
        # Unix/Linux/Mac
        import subprocess
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'train_from_csv'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                print(f"✅ Found {len(pids)} training process(es): {', '.join(pids)}")
                print("🟢 Status: TRAINING IS RUNNING")
                return True
            else:
                print("❌ No training processes found")
                return False
        except Exception as e:
            print(f"Error checking process: {e}")
            return None

def check_training_output():
    """Check for training output files to see progress."""
    models_dir = Path(__file__).parent / "backend" / "trained_models"
    
    print(f"\nChecking for model outputs in: {models_dir}")
    
    if not models_dir.exists():
        print("   Models directory doesn't exist yet")
        return
    
    # Check for best model (saved during training)
    best_model = models_dir / "best_similarity_model"
    if best_model.exists():
        print(f"   ✓ Found best similarity model (training is progressing)")
        # Check modification time
        import datetime
        mod_time = datetime.datetime.fromtimestamp(best_model.stat().st_mtime)
        print(f"   Last updated: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check for final model
    final_model = models_dir / "fine-tuned-resume-matcher"
    if final_model.exists():
        print(f"   ✓ Found final similarity model (training completed!)")
    
    # Check for category classifier
    classifier = models_dir / "category_classifier_optimized"
    if classifier.exists():
        print(f"   ✓ Found category classifier (training completed!)")

if __name__ == "__main__":
    print("="*60)
    print("Training Status Check")
    print("="*60)
    
    # Check if process is running
    is_running = check_training_status()
    
    # Check for output files
    check_training_output()
    
    print("\n" + "="*60)
    print("Tips:")
    print("  - First epoch with 7000 samples can take 5-15 minutes")
    print("  - Progress bar is disabled, but training is happening")
    print("  - Check Task Manager (Windows) to see CPU/Memory usage")
    print("  - Training will print results when epoch completes")
    print("="*60)





