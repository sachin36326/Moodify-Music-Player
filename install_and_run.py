# install_and_run.py - Run this FIRST
import subprocess
import sys
import os

def install_packages():
    print("🔧 Installing required packages...")
    packages = ['requests', 'pygame', 'pillow']
    
    for package in packages:
        print(f"\nInstalling {package}...")
        try:
            # Try pip install
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except Exception as e:
            print(f"⚠️ Error installing {package}: {e}")
            # Try alternative
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user"])
                print(f"✅ {package} installed with --user flag")
            except:
                print(f"❌ Failed to install {package}")
    
    print("\n" + "="*50)
    print("✅ All packages installed! Now running Moodify...")
    print("="*50)
    
    # Run moodify.py
    try:
        import moodify
    except ImportError:
        print("\nRunning moodify directly...")
        os.system(f'python moodify.py')

if __name__ == "__main__":
    install_packages()