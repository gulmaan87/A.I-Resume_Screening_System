"""
Setup script to install required packages for category classification training.
"""

import subprocess
import sys

def install_packages():
    """Install required packages for training."""
    packages = [
        "sentence-transformers",
        "scikit-learn",
        "numpy",
        "pandas",
    ]
    
    print("Installing required packages for training...")
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    print("\n✅ All packages installed successfully!")
    return True

if __name__ == "__main__":
    if install_packages():
        print("\nYou can now run the training script:")
        print('python -m app.scripts.train_category_classifier "path/to/dataset.csv"')
    else:
        print("\n❌ Some packages failed to install. Please install manually:")
        print("pip install sentence-transformers scikit-learn numpy pandas")

