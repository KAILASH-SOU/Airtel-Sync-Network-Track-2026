import os
import sys
import webbrowser

from benchmark import run_full_benchmark

def main():
    print("\n" + "=" * 75)
    print("  AIRTEL SYNC: NETWORK CASE STUDY 1 PROTOTYPE SUITE")
    print("  Stadium Surge: 5G Capacity for a 1,00,000-Fan World Cup Final")
    print("  Made by NIT Nagpur Final Year Students")
    print("=" * 75)

    run_full_benchmark()

    html_path = os.path.abspath("stadium_twin.html")
    print("=" * 75)
    print("PROTOTYPE LAUNCH OPTIONS:")
    print("=" * 75)
    print(f"1. Standalone Direct Browser View (Zero dependencies):")
    print(f"   Open file in any browser:  file://{html_path}\n")
    print(f"2. Local Python Server (with REST API):")
    print(f"   Run:  python3 server.py")
    print(f"   Then open:  http://localhost:8501/\n")
    print(f"3. Native Streamlit Mode (for Cloud Deployment):")
    print(f"   Run:  streamlit run app.py\n")
    print("=" * 75)

if __name__ == "__main__":
    main()
