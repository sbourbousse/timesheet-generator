import os
import yaml
from pathlib import Path


class Config:
    """Classe de gestion de la configuration de l'application."""
    
    def __init__(self, config_path=None):
        self.config_path = config_path or Path("config.yaml")
        self.config = self._load_config()
    
    def _load_config(self):
        """Charge la configuration depuis le fichier YAML."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return self._default_config()
    
    def _default_config(self):
        """Retourne la configuration par défaut."""
        return {
            "repositories": [],
            "authors": [],
            "ticket_pattern": r'([A-Z]+-\d+)',
            "export_path": "exports",
            "work_hours_per_day": 8,
            "work_periods": {
                "morning": {"start": "09:00", "end": "13:00"},
                "afternoon": {"start": "14:00", "end": "18:00"}
            }
        }
    
    def save_config(self):
        """Sauvegarde la configuration dans le fichier YAML."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def get_repositories(self):
        """Retourne la liste des dépôts configurés."""
        return self.config.get("repositories", [])
    
    def add_repository(self, path):
        """Ajoute un dépôt à la configuration."""
        if "repositories" not in self.config:
            self.config["repositories"] = []
        if path not in self.config["repositories"]:
            self.config["repositories"].append(path)
            self.save_config()
    
    def remove_repository(self, path):
        """Supprime un dépôt de la configuration."""
        if "repositories" in self.config and path in self.config["repositories"]:
            self.config["repositories"].remove(path)
            self.save_config()
    
    def get_authors(self):
        """Retourne la liste des auteurs configurés."""
        return self.config.get("authors", [])
    
    def add_author(self, author):
        """Ajoute un auteur à la configuration."""
        if "authors" not in self.config:
            self.config["authors"] = []
        if author not in self.config["authors"]:
            self.config["authors"].append(author)
            self.save_config()
    
    def remove_author(self, author):
        """Supprime un auteur de la configuration."""
        if "authors" in self.config and author in self.config["authors"]:
            self.config["authors"].remove(author)
            self.save_config()
    
    def get_ticket_pattern(self):
        """Retourne le pattern pour extraire les tickets."""
        return self.config.get("ticket_pattern", r'([A-Z]+-\d+)')
    
    def set_ticket_pattern(self, pattern):
        """Définit le pattern pour extraire les tickets."""
        self.config["ticket_pattern"] = pattern
        self.save_config()
    
    def get_export_path(self):
        """Retourne le chemin d'exportation."""
        return self.config.get("export_path", "exports")
    
    def set_export_path(self, path):
        """Définit le chemin d'exportation."""
        self.config["export_path"] = path
        self.save_config()
    
    def get_work_hours_per_day(self):
        """Retourne le nombre d'heures de travail par jour."""
        return self.config.get("work_hours_per_day", 8)
    
    def set_work_hours_per_day(self, hours):
        """Définit le nombre d'heures de travail par jour."""
        self.config["work_hours_per_day"] = hours
        self.save_config()
    
    def get_work_periods(self):
        """Retourne les plages horaires de travail (matin et après-midi)."""
        return self.config.get("work_periods", {
            "morning": {"start": "09:00", "end": "13:00"},
            "afternoon": {"start": "14:00", "end": "18:00"}
        })

    def set_work_periods(self, morning_start, morning_end, afternoon_start, afternoon_end):
        """Définit les plages horaires de travail (matin et après-midi)."""
        self.config["work_periods"] = {
            "morning": {"start": morning_start, "end": morning_end},
            "afternoon": {"start": afternoon_start, "end": afternoon_end}
        }
        self.save_config() 