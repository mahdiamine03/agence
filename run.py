import sys
import os

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.main import TravelApp
except ModuleNotFoundError as e:
    print("\nError: Missing Dependencies.")
    print(f"Details: {e}")
    print("\nPlease run: pip install -r requirements.txt\n")
    input("Press Enter to exit...")
    sys.exit(1)

if __name__ == "__main__":
    app = TravelApp()
    app.mainloop()
