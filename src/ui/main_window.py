import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QFileDialog,
    QTabWidget, QMessageBox, QHeaderView, QGroupBox, QFormLayout,
    QLineEdit, QListWidget, QListWidgetItem, QComboBox, QDateEdit,
    QInputDialog
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QBrush, QColor, QFont

from src.core.git_processor import GitProcessor
from src.core.ticket_analyzer import TicketAnalyzer
from src.core.timesheet_generator import TimesheetGenerator
from src.ui.config_dialog import ConfigDialog


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""
    
    def __init__(self, config):
        super().__init__()
        
        self.config = config
        self.git_processor = GitProcessor(config)
        self.ticket_analyzer = TicketAnalyzer(config)
        self.timesheet_generator = TimesheetGenerator(config)
        
        self.durees_par_journee = {}
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle("Générateur de Timesheet")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central et layout principal
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Onglets
        tabs = QTabWidget()
        tabs.addTab(self.create_generation_tab(), "Génération de Timesheet")
        tabs.addTab(self.create_configuration_tab(), "Configuration")
        
        main_layout.addWidget(tabs)
        
        self.setCentralWidget(central_widget)
        
        # Statut
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Prêt")
        
        # Activer le bouton Analyser les tickets si le fichier git_logs.csv existe déjà
        logs_file = self.git_processor.logs_file
        if os.path.exists(logs_file):
            self.btn_analyze_tickets.setEnabled(True)
            self.show_last_extraction_time()
    
    def create_generation_tab(self):
        """Crée l'onglet de génération de timesheet."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Label pour la dernière extraction (ligne séparée)
        self.last_extraction_label = QLabel("")
        layout.addWidget(self.last_extraction_label)
        
        # Boutons d'action
        actions_layout = QHBoxLayout()
        
        self.btn_extract_logs = QPushButton("Extraire les logs Git")
        self.btn_extract_logs.clicked.connect(self.extract_git_logs)
        actions_layout.addWidget(self.btn_extract_logs)
        
        self.btn_analyze_tickets = QPushButton("Analyser les tickets")
        self.btn_analyze_tickets.clicked.connect(self.analyze_tickets)
        self.btn_analyze_tickets.setEnabled(False)
        actions_layout.addWidget(self.btn_analyze_tickets)
        
        self.btn_generate_json = QPushButton("Générer JSON")
        self.btn_generate_json.clicked.connect(self.generate_json)
        self.btn_generate_json.setEnabled(False)
        actions_layout.addWidget(self.btn_generate_json)
        
        self.btn_generate_xml = QPushButton("Générer XML")
        self.btn_generate_xml.clicked.connect(self.generate_xml)
        self.btn_generate_xml.setEnabled(False)
        actions_layout.addWidget(self.btn_generate_xml)
        
        layout.addLayout(actions_layout)
        
        # Filtres
        filters_group = QGroupBox("Filtres")
        filters_layout = QFormLayout(filters_group)
        
        # Filtres de dates
        date_layout = QHBoxLayout()
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        date_layout.addWidget(QLabel("Du"))
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(QLabel("au"))
        date_layout.addWidget(self.date_to)
        date_layout.addStretch()
        
        filters_layout.addRow("Période", date_layout)
        
        # Filtre d'auteurs
        author_layout = QHBoxLayout()
        self.author_combo = QComboBox()
        self.update_author_combo()
        author_layout.addWidget(self.author_combo)
        author_layout.addStretch()
        
        filters_layout.addRow("Auteur", author_layout)
        
        layout.addWidget(filters_group)
        
        # Tableau des résultats
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Ticket", "Durée (heures)", "Heure de début", "Heure de fin"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        return tab
    
    def create_configuration_tab(self):
        """Crée l'onglet de configuration."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Configuration des dépôts
        repos_group = QGroupBox("Dépôts Git")
        repos_layout = QVBoxLayout(repos_group)
        
        self.repos_list = QListWidget()
        self.update_repos_list()
        repos_layout.addWidget(self.repos_list)
        
        repos_buttons_layout = QHBoxLayout()
        self.btn_add_repo = QPushButton("Ajouter")
        self.btn_add_repo.clicked.connect(self.add_repository)
        repos_buttons_layout.addWidget(self.btn_add_repo)
        
        self.btn_remove_repo = QPushButton("Supprimer")
        self.btn_remove_repo.clicked.connect(self.remove_repository)
        repos_buttons_layout.addWidget(self.btn_remove_repo)
        
        repos_layout.addLayout(repos_buttons_layout)
        layout.addWidget(repos_group)
        
        # Configuration des auteurs
        authors_group = QGroupBox("Auteurs")
        authors_layout = QVBoxLayout(authors_group)
        
        self.authors_list = QListWidget()
        self.update_authors_list()
        authors_layout.addWidget(self.authors_list)
        
        authors_buttons_layout = QHBoxLayout()
        self.btn_add_author = QPushButton("Ajouter")
        self.btn_add_author.clicked.connect(self.add_author)
        authors_buttons_layout.addWidget(self.btn_add_author)
        
        self.btn_remove_author = QPushButton("Supprimer")
        self.btn_remove_author.clicked.connect(self.remove_author)
        authors_buttons_layout.addWidget(self.btn_remove_author)
        
        authors_layout.addLayout(authors_buttons_layout)
        layout.addWidget(authors_group)
        
        # Autres configurations
        other_config_group = QGroupBox("Autres configurations")
        other_config_layout = QFormLayout(other_config_group)
        
        self.pattern_edit = QLineEdit(self.config.get_ticket_pattern())
        self.pattern_edit.textChanged.connect(self.update_ticket_pattern)
        other_config_layout.addRow("Pattern de ticket:", self.pattern_edit)
        # Champs horaires de travail matin/après-midi
        work_periods = self.config.get_work_periods()
        self.morning_start_edit = QLineEdit(work_periods['morning']['start'])
        self.morning_end_edit = QLineEdit(work_periods['morning']['end'])
        self.afternoon_start_edit = QLineEdit(work_periods['afternoon']['start'])
        self.afternoon_end_edit = QLineEdit(work_periods['afternoon']['end'])
        self.morning_start_edit.editingFinished.connect(self.update_work_periods)
        self.morning_end_edit.editingFinished.connect(self.update_work_periods)
        self.afternoon_start_edit.editingFinished.connect(self.update_work_periods)
        self.afternoon_end_edit.editingFinished.connect(self.update_work_periods)
        other_config_layout.addRow("Début matin (HH:mm):", self.morning_start_edit)
        other_config_layout.addRow("Fin matin (HH:mm):", self.morning_end_edit)
        other_config_layout.addRow("Début après-midi (HH:mm):", self.afternoon_start_edit)
        other_config_layout.addRow("Fin après-midi (HH:mm):", self.afternoon_end_edit)
        
        self.export_path_edit = QLineEdit(self.config.get_export_path())
        self.export_path_edit.setReadOnly(True)
        export_path_layout = QHBoxLayout()
        export_path_layout.addWidget(self.export_path_edit)
        self.btn_browse_export = QPushButton("Parcourir")
        self.btn_browse_export.clicked.connect(self.browse_export_path)
        export_path_layout.addWidget(self.btn_browse_export)
        other_config_layout.addRow("Chemin d'exportation:", export_path_layout)
        
        layout.addWidget(other_config_group)
        
        return tab
    
    def update_repos_list(self):
        """Met à jour la liste des dépôts."""
        self.repos_list.clear()
        for repo in self.config.get_repositories():
            item = QListWidgetItem(repo)
            self.repos_list.addItem(item)
    
    def update_authors_list(self):
        """Met à jour la liste des auteurs."""
        self.authors_list.clear()
        for author in self.config.get_authors():
            item = QListWidgetItem(author)
            self.authors_list.addItem(item)
    
    def update_author_combo(self):
        """Met à jour la liste déroulante des auteurs."""
        self.author_combo.clear()
        self.author_combo.addItem("Tous")
        for author in self.config.get_authors():
            self.author_combo.addItem(author)
    
    def add_repository(self):
        """Ajoute un dépôt Git à la configuration."""
        repo_path = QFileDialog.getExistingDirectory(self, "Sélectionner un dépôt Git")
        if repo_path:
            self.config.add_repository(repo_path)
            self.update_repos_list()
    
    def remove_repository(self):
        """Supprime le dépôt Git sélectionné de la configuration."""
        selected_items = self.repos_list.selectedItems()
        if selected_items:
            repo_path = selected_items[0].text()
            self.config.remove_repository(repo_path)
            self.update_repos_list()
    
    def add_author(self):
        """Ajoute un auteur à la configuration."""
        author, ok = QInputDialog.getText(self, "Ajouter un auteur", "Nom de l'auteur:")
        if ok and author:
            self.config.add_author(author)
            self.update_authors_list()
            self.update_author_combo()
    
    def remove_author(self):
        """Supprime l'auteur sélectionné de la configuration."""
        selected_items = self.authors_list.selectedItems()
        if selected_items:
            author = selected_items[0].text()
            self.config.remove_author(author)
            self.update_authors_list()
            self.update_author_combo()
    
    def update_ticket_pattern(self, pattern):
        """Met à jour le pattern de ticket dans la configuration."""
        self.config.set_ticket_pattern(pattern)
    
    def update_work_periods(self):
        """Met à jour les horaires de travail matin/après-midi dans la configuration."""
        self.config.set_work_periods(
            self.morning_start_edit.text(),
            self.morning_end_edit.text(),
            self.afternoon_start_edit.text(),
            self.afternoon_end_edit.text()
        )
    
    def browse_export_path(self):
        """Permet de sélectionner le chemin d'exportation."""
        export_path = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier d'exportation")
        if export_path:
            self.config.set_export_path(export_path)
            self.export_path_edit.setText(export_path)
    
    def extract_git_logs(self):
        """Extrait les logs Git."""
        self.status_bar.showMessage("Extraction des logs Git en cours...")
        
        try:
            logs_file = self.git_processor.extract_git_logs()
            self.status_bar.showMessage(f"Logs Git extraits dans {logs_file}")
            self.btn_analyze_tickets.setEnabled(True)
            self.show_last_extraction_time()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'extraction des logs Git : {str(e)}")
            self.status_bar.showMessage("Erreur lors de l'extraction des logs Git")
    
    def show_last_extraction_time(self):
        """Affiche la date/heure de la dernière extraction des logs Git sous forme relative dans un label au-dessus des boutons."""
        import os
        import datetime
        logs_file = self.git_processor.logs_file
        if os.path.exists(logs_file):
            mtime = os.path.getmtime(logs_file)
            dt = datetime.datetime.fromtimestamp(mtime)
            now = datetime.datetime.now()
            delta = now - dt
            if delta.days > 1:
                msg = f"Dernière extraction des logs Git : il y a {delta.days} jours"
            elif delta.days == 1:
                msg = "Dernière extraction des logs Git : il y a 1 jour"
            elif delta.seconds >= 7200:
                heures = delta.seconds // 3600
                msg = f"Dernière extraction des logs Git : il y a {heures} heures"
            elif delta.seconds >= 3600:
                msg = "Dernière extraction des logs Git : il y a 1 heure"
            elif delta.seconds >= 120:
                minutes = delta.seconds // 60
                msg = f"Dernière extraction des logs Git : il y a {minutes} minutes"
            elif delta.seconds >= 60:
                msg = "Dernière extraction des logs Git : il y a 1 minute"
            else:
                msg = "Dernière extraction des logs Git : à l'instant"
            self.last_extraction_label.setText(msg)
    
    def analyze_tickets(self):
        """Analyse les tickets à partir des logs Git."""
        self.status_bar.showMessage("Analyse des tickets en cours...")
        
        try:
            # Charger les logs Git dans un DataFrame
            df = self.git_processor.load_git_logs_dataframe()
            
            # Filtrer par dates si spécifiées
            date_from = self.date_from.date().toPyDate()
            date_to = self.date_to.date().toPyDate()
            df = df[(df['date'].dt.date >= date_from) & (df['date'].dt.date <= date_to)]
            
            # Filtrer par auteur si spécifié
            selected_author = self.author_combo.currentText()
            if selected_author != "Tous":
                df = df[df['author'] == selected_author]
            
            # Analyser les tickets
            self.durees_par_journee = self.ticket_analyzer.extract_tickets_from_dataframe(df)
            self.durees_par_journee = self.ticket_analyzer.adjust_durations(self.durees_par_journee)
            
            # Mettre à jour le tableau
            self.update_table()
            
            self.status_bar.showMessage("Analyse des tickets terminée")
            self.btn_generate_json.setEnabled(True)
            self.btn_generate_xml.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'analyse des tickets : {str(e)}")
            self.status_bar.showMessage("Erreur lors de l'analyse des tickets")
    
    def update_table(self):
        """Met à jour le tableau avec les durées par journée."""
        self.table.setRowCount(0)  # Vider le tableau
        row = 0
        for journee, tickets in sorted(self.durees_par_journee.items()):
            # Ligne de titre pour le jour
            self.table.insertRow(row)
            title_item = QTableWidgetItem(str(journee))
            title_item.setFont(QFont('Arial', weight=QFont.Bold))
            title_item.setBackground(QBrush(QColor(220, 220, 220)))  # gris clair
            title_item.setTextAlignment(Qt.AlignCenter)
            self.table.setSpan(row, 0, 1, 5)
            self.table.setItem(row, 0, title_item)
            row += 1
            for t in tickets:
                try:
                    self.table.insertRow(row)
                    # Date (vide car déjà dans le titre)
                    date_item = QTableWidgetItem("")
                    self.table.setItem(row, 0, date_item)
                    # Ticket
                    ticket_item = QTableWidgetItem(t.get('ticket', '?'))
                    ticket_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, 1, ticket_item)
                    # Durée (format HH:MM, jamais négatif)
                    duree = t.get('duree')
                    if duree is None or not hasattr(duree, 'total_seconds'):
                        duree = duree.__class__() if duree else __import__('datetime').timedelta(0)
                    if duree.total_seconds() < 0:
                        duree = duree.__class__()  # timedelta(0)
                    heures = int(duree.total_seconds() // 3600)
                    minutes = int((duree.total_seconds() % 3600) // 60)
                    duree_str = f"{heures:02d}:{minutes:02d}"
                    duree_item = QTableWidgetItem(duree_str)
                    duree_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, 2, duree_item)
                    # Heure de début
                    heure_debut = t.get('debut')
                    heure_debut_str = heure_debut.strftime('%H:%M') if hasattr(heure_debut, 'strftime') else ''
                    debut_item = QTableWidgetItem(heure_debut_str)
                    debut_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, 3, debut_item)
                    # Heure de fin
                    heure_fin = t.get('fin')
                    heure_fin_str = heure_fin.strftime('%H:%M') if hasattr(heure_fin, 'strftime') else ''
                    fin_item = QTableWidgetItem(heure_fin_str)
                    fin_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, 4, fin_item)
                    # Coloration matin/après-midi/erreur
                    color = None
                    if t.get('erreur', False):
                        color = QColor(255, 150, 150)  # rouge clair
                    else:
                        # Récupérer les bornes matin/aprem
                        from datetime import datetime
                        work_periods = self.config.get_work_periods()
                        morning_end = work_periods['morning']['end']
                        afternoon_start = work_periods['afternoon']['start']
                        heure_debut_val = heure_debut_str
                        if heure_debut_val:
                            if heure_debut_val < morning_end:
                                color = QColor(200, 255, 200)  # vert clair
                            elif heure_debut_val >= afternoon_start:
                                color = QColor(200, 220, 255)  # bleu clair
                    if color:
                        for col in range(5):
                            self.table.item(row, col).setBackground(QBrush(color))
                except Exception:
                    self.table.insertRow(row)
                    for col in range(5):
                        item = QTableWidgetItem('Erreur')
                        item.setBackground(Qt.red)
                        self.table.setItem(row, col, item)
                row += 1
    
    def generate_json(self):
        """Génère un fichier JSON avec les durées par journée."""
        self.status_bar.showMessage("Génération du fichier JSON en cours...")
        
        try:
            output_file = self.timesheet_generator.generate_json(self.durees_par_journee)
            self.status_bar.showMessage(f"Fichier JSON généré : {output_file}")
            
            # Demander si l'utilisateur veut ouvrir le fichier
            reply = QMessageBox.question(
                self, "Fichier généré", 
                f"Le fichier JSON a été généré avec succès :\n{output_file}\n\nVoulez-vous l'ouvrir ?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                os.startfile(output_file)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération du fichier JSON : {str(e)}")
            self.status_bar.showMessage("Erreur lors de la génération du fichier JSON")
    
    def generate_xml(self):
        """Génère un fichier XML avec les durées par journée."""
        self.status_bar.showMessage("Génération du fichier XML en cours...")
        
        try:
            output_file = self.timesheet_generator.generate_xml(self.durees_par_journee)
            self.status_bar.showMessage(f"Fichier XML généré : {output_file}")
            
            # Demander si l'utilisateur veut ouvrir le fichier
            reply = QMessageBox.question(
                self, "Fichier généré", 
                f"Le fichier XML a été généré avec succès :\n{output_file}\n\nVoulez-vous l'ouvrir ?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                os.startfile(output_file)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération du fichier XML : {str(e)}")
            self.status_bar.showMessage("Erreur lors de la génération du fichier XML") 