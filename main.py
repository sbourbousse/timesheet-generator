import sys
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.config import Config

def main():
    """Point d'entrée principal de l'application."""
    # Charger la configuration
    config = Config()
    
    # Initialiser l'application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Style moderne et cohérent
    
    # Créer et afficher la fenêtre principale
    window = MainWindow(config)
    window.show()
    
    # Exécuter l'application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 