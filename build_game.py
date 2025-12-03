import os
import sys
import subprocess
import shutil

print("="*60)
print("Stock Market Game - Simple Build Script")
print("="*60 + "\n")

# Clean old builds
print("🗑️  Cleaning old build files...")
for folder in ['build', '__pycache__']:
    if os.path.exists(folder):
        try:
            shutil.rmtree(folder)
            print(f"   Removed {folder}/")
        except:
            pass

for spec_file in [f for f in os.listdir('.') if f.endswith('.spec')]:
    try:
        os.remove(spec_file)
        print(f"   Removed {spec_file}")
    except:
        pass

print("\n🔨 Building executable...")
print("This will take 5-15 minutes. Please be patient!\n")

# Determine separator based on OS
separator = ';' if sys.platform == 'win32' else ':'

# Build command
cmd = [
    'pyinstaller',
    '--name=StockMarketGame',
    '--windowed',
    '--onefile',
    '--distpath=.',
    f'--add-data=images{separator}images',
    f'--add-data=sounds{separator}sounds',
    '--hidden-import=PySide6',
    '--hidden-import=openai',
    '--hidden-import=pandas',
    '--hidden-import=yfinance',
    '--hidden-import=matplotlib',
    '--hidden-import=python-dotenv',
    '--collect-all=PySide6',
    '--noconfirm',
    'Game_code/main.py'
]

# Add .env if exists
if os.path.exists('.env'):
    cmd.insert(-1, f'--add-data=.env{separator}.')

# Add icon if exists
if os.path.exists('images/logo.ico'):
    cmd.insert(-1, '--icon=images/logo.ico')

# Run build
try:
    subprocess.run(cmd, check=True)

    print("\n" + "="*60)
    print("🎉 BUILD SUCCESSFUL!")
    print("="*60)

    # Find executable
    if sys.platform == 'win32':
        exe = 'StockMarketGame.exe'
    elif sys.platform == 'darwin':
        exe = 'StockMarketGame.app'
    else:
        exe = 'StockMarketGame'

    if os.path.exists(exe):
        size_mb = os.path.getsize(exe) / (1024 * 1024)
        print(f"\n📦 Executable: {exe}")
        print(f"📊 Size: {size_mb:.2f} MB")

    print("\n✅ Your game is ready to play!")
    print("="*60)

except subprocess.CalledProcessError as e:
    print("\n❌ BUILD FAILED!")
    print("Check the error messages above.")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)