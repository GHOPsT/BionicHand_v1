# bionic_hand/main.py
import sys
from pathlib import Path

# Agrega la carpeta padre al path de Python automáticamente
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.hand import BionicHand
from visualization.visualizer import BionicHandVisualizer

def main():
    print("Iniciando BionicHand — Prototipo Cinemático y de Control Lógico (Etapa 1)...")
    hand = BionicHand()
    visualizer = BionicHandVisualizer(hand)
    visualizer.show()

if __name__ == "__main__":
    main()