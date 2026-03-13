"""
Check and install required dependencies for Facebook/Instagram integration
"""

import subprocess
import sys


def check_package(package_name):
    """Check if a package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def install_package(package_name):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Check and install required packages"""
    print("\n" + "="*60)
    print("FACEBOOK/INSTAGRAM INTEGRATION - DEPENDENCY CHECK")
    print("="*60 + "\n")

    required_packages = {
        "requests": "requests",
        "dotenv": "python-dotenv",
    }

    missing_packages = []
    installed_packages = []

    # Check which packages are missing
    for import_name, package_name in required_packages.items():
        if check_package(import_name):
            print(f"✅ {package_name} - Already installed")
            installed_packages.append(package_name)
        else:
            print(f"❌ {package_name} - Not installed")
            missing_packages.append(package_name)

    if not missing_packages:
        print("\n🎉 All required packages are installed!")
        return True

    # Ask to install missing packages
    print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
    response = input("\nDo you want to install missing packages? (yes/no): ").lower()

    if response != 'yes':
        print("\n⏭️  Skipping installation")
        print("\nTo install manually, run:")
        for package in missing_packages:
            print(f"  pip install {package}")
        return False

    # Install missing packages
    print("\n📥 Installing packages...")
    success_count = 0

    for package in missing_packages:
        print(f"\nInstalling {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
            success_count += 1
        else:
            print(f"❌ Failed to install {package}")

    # Summary
    print("\n" + "="*60)
    if success_count == len(missing_packages):
        print("🎉 All packages installed successfully!")
        return True
    else:
        print(f"⚠️  Installed {success_count}/{len(missing_packages)} packages")
        print("\nPlease install missing packages manually")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Installation failed: {e}\n")
        sys.exit(1)
