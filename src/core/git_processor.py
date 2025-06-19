import subprocess
import csv
import os
from datetime import datetime
import pandas as pd


class GitProcessor:
    """Classe pour traiter les logs Git et extraire les informations pertinentes."""
    
    def __init__(self, config):
        """
        Initialise le processeur Git.
        
        Args:
            config: L'objet de configuration contenant les informations nécessaires.
        """
        self.config = config
        self.logs_file = "git_logs.csv"
        self.delimiter = '›'
    
    def run_git_command(self, repo_path, command):
        """
        Exécute une commande Git dans le répertoire spécifié.
        
        Args:
            repo_path: Le chemin du dépôt Git.
            command: La commande Git à exécuter.
            
        Returns:
            Le résultat de la commande.
        """
        full_command = f"git -C {repo_path} {command}"
        process = subprocess.Popen(full_command, stdout=subprocess.PIPE, shell=True)
        output = process.communicate()[0].strip()
        return output.decode("utf-8")
    
    def extract_git_logs(self, output_file=None):
        """
        Extrait les logs Git de tous les dépôts configurés.
        
        Args:
            output_file: Le fichier de sortie pour les logs Git.
            
        Returns:
            Le chemin du fichier contenant les logs Git.
        """
        output_file = output_file or self.logs_file
        
        # Si le fichier existe déjà, le supprimer
        if os.path.exists(output_file):
            os.remove(output_file)
        
        # Mettre à jour chaque dépôt avant d'extraire les logs
        for repo_path in self.config.get_repositories():
            # Faire un git pull pour mettre à jour le dépôt
            self.run_git_command(repo_path, 'pull')
            # Extraire les logs de toutes les branches (--all)
            command = f'log --all --pretty=format:"%h{self.delimiter}%an{self.delimiter}%ad{self.delimiter}%s" --date=format:"%Y-%m-%d %H:%M"'
            logs = self.run_git_command(repo_path, command)
            
            # Écrire les logs dans le fichier
            write_mode = 'a' if os.path.exists(output_file) else 'w'
            with open(output_file, write_mode, newline='', encoding='utf-8') as f:
                f.write(logs)
                if logs:  # Ajouter une nouvelle ligne si les logs ne sont pas vides
                    f.write('\n')
        
        # Nettoyer les lignes problématiques
        self.clean_logs_file(output_file)
        
        return output_file
    
    def clean_logs_file(self, logs_file):
        """
        Nettoie le fichier de logs en supprimant les lignes avec trop de colonnes.
        
        Args:
            logs_file: Le fichier de logs à nettoyer.
        """
        clean_rows = []
        
        # Lire toutes les lignes du fichier
        with open(logs_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter)
            for row in reader:
                if len(row) == 4:  # Conserver uniquement les lignes avec 4 colonnes
                    clean_rows.append(row)
        
        # Réécrire le fichier avec les lignes nettoyées
        with open(logs_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=self.delimiter)
            writer.writerows(clean_rows)
    
    def load_git_logs_dataframe(self, logs_file=None):
        """
        Charge les logs Git dans un DataFrame pandas.
        
        Args:
            logs_file: Le fichier contenant les logs Git.
            
        Returns:
            Un DataFrame pandas contenant les logs Git.
        """
        logs_file = logs_file or self.logs_file
        
        # Charger les données dans un DataFrame
        df = pd.read_csv(
            logs_file,
            names=['hash', 'author', 'date', 'message'],
            parse_dates=['date'],
            delimiter=self.delimiter,
            engine='python'  # Nécessaire pour les délimiteurs multi-caractères
        )
        
        # Filtrer par auteur
        authors = self.config.get_authors()
        if authors:
            df = df[df['author'].isin(authors)]
        
        # Trier par date (du plus ancien au plus récent)
        df = df.sort_values(by=['date'])
        
        return df 