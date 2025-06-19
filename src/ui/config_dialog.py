from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFormLayout, QDialogButtonBox, QFileDialog
)

class ConfigDialog(QDialog):
    """Boîte de dialogue de configuration."""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle("Configuration")
        self.setGeometry(300, 300, 500, 250)
        
        layout = QVBoxLayout(self)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Pattern de ticket
        self.pattern_edit = QLineEdit(self.config.get_ticket_pattern())
        form_layout.addRow("Pattern de ticket:", self.pattern_edit)
        
        # Horaires de travail matin
        work_periods = self.config.get_work_periods()
        self.morning_start_edit = QLineEdit(work_periods['morning']['start'])
        self.morning_end_edit = QLineEdit(work_periods['morning']['end'])
        self.afternoon_start_edit = QLineEdit(work_periods['afternoon']['start'])
        self.afternoon_end_edit = QLineEdit(work_periods['afternoon']['end'])
        form_layout.addRow("Début matin (HH:mm):", self.morning_start_edit)
        form_layout.addRow("Fin matin (HH:mm):", self.morning_end_edit)
        form_layout.addRow("Début après-midi (HH:mm):", self.afternoon_start_edit)
        form_layout.addRow("Fin après-midi (HH:mm):", self.afternoon_end_edit)
        
        # Champ heures de travail par jour désactivé
        self.hours_edit = QLineEdit(str(self.config.get_work_hours_per_day()))
        self.hours_edit.setDisabled(True)
        form_layout.addRow("Heures de travail par jour (désactivé):", self.hours_edit)
        
        # Chemin d'exportation
        self.export_path_edit = QLineEdit(self.config.get_export_path())
        export_path_layout = QHBoxLayout()
        export_path_layout.addWidget(self.export_path_edit)
        self.btn_browse_export = QPushButton("Parcourir")
        self.btn_browse_export.clicked.connect(self.browse_export_path)
        export_path_layout.addWidget(self.btn_browse_export)
        form_layout.addRow("Chemin d'exportation:", export_path_layout)
        
        layout.addLayout(form_layout)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def browse_export_path(self):
        """Permet de sélectionner le chemin d'exportation."""
        export_path = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier d'exportation")
        if export_path:
            self.export_path_edit.setText(export_path)
    
    def accept(self):
        """Sauvegarde les changements lors de la validation."""
        # Mettre à jour la configuration
        self.config.set_ticket_pattern(self.pattern_edit.text())
        
        # Horaires de travail matin/après-midi
        self.config.set_work_periods(
            self.morning_start_edit.text(),
            self.morning_end_edit.text(),
            self.afternoon_start_edit.text(),
            self.afternoon_end_edit.text()
        )
        
        self.config.set_export_path(self.export_path_edit.text())
        
        # Sauvegarder la configuration
        self.config.save_config()
        
        super().accept() 