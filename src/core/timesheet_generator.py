import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
from datetime import datetime


class TimesheetGenerator:
    """Classe pour générer des feuilles de temps à partir des données d'analyse de tickets."""
    
    def __init__(self, config):
        """
        Initialise le générateur de feuilles de temps.
        
        Args:
            config: L'objet de configuration contenant les informations nécessaires.
        """
        self.config = config
        self.export_path = self.config.get_export_path()
        
        # Créer le répertoire d'exportation s'il n'existe pas
        if not os.path.exists(self.export_path):
            os.makedirs(self.export_path)
    
    def generate_json(self, durees_par_journee, output_file=None):
        """
        Génère un fichier JSON à partir des durées par journée.
        
        Args:
            durees_par_journee: Un dictionnaire {jour: [tickets]} où chaque ticket est un dict.
            output_file: Le nom du fichier de sortie.
            
        Returns:
            Le chemin du fichier JSON généré.
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.export_path, f"timesheet_{timestamp}.json")
        json_array = []
        for journee, tickets in durees_par_journee.items():
            day = str(journee)
            day_data = {
                "day": day,
                "tickets": []
            }
            for t in tickets:
                duration = str(t['duree'].total_seconds())
                day_data["tickets"].append({
                    "code": t['ticket'],
                    "duration": duration,
                    "start": t['debut'].strftime('%H:%M'),
                    "end": t['fin'].strftime('%H:%M'),
                    "message": t['message']
                })
            json_array.append(day_data)
        with open(output_file, 'w', encoding='utf-8') as fp:
            json.dump(json_array, fp, indent=4, sort_keys=True, default=str)
        return output_file
    
    def generate_xml(self, durees_par_journee, output_file=None):
        """
        Génère un fichier XML à partir des durées par journée.
        
        Args:
            durees_par_journee: Un dictionnaire {jour: [tickets]} où chaque ticket est un dict.
            output_file: Le nom du fichier de sortie.
            
        Returns:
            Le chemin du fichier XML généré.
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.export_path, f"timesheet_{timestamp}.xml")
        root = ET.Element('timesheet')
        for journee, tickets in durees_par_journee.items():
            day = ET.SubElement(root, 'day', date=str(journee))
            for t in tickets:
                ET.SubElement(day, 'ticket', 
                    code=t['ticket'], 
                    duration=str(t['duree'].total_seconds()), 
                    start=t['debut'].strftime('%H:%M'), 
                    end=t['fin'].strftime('%H:%M'),
                    message=t['message'])
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xmlstr)
        return output_file 