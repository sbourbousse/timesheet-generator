import re
from datetime import datetime, timedelta


class TicketAnalyzer:
    """Classe pour analyser les tickets à partir des logs Git."""
    
    def __init__(self, config):
        """
        Initialise l'analyseur de tickets.
        
        Args:
            config: L'objet de configuration contenant les informations nécessaires.
        """
        self.config = config
        self.ticket_pattern = re.compile(config.get_ticket_pattern())
    
    def extract_tickets_from_dataframe(self, df):
        """
        Extrait les tickets et calcule le temps passé à partir d'un DataFrame.
        
        Args:
            df: Un DataFrame pandas contenant les logs Git.
            
        Returns:
            Un dictionnaire des infos par journée et par ticket : durée, heure de début, heure de fin.
            Si un ticket chevauche la pause déjeuner, il est dupliqué (avant et après la pause).
        """
        work_periods = self.config.get_work_periods()
        morning_start = work_periods['morning']['start']
        morning_end = work_periods['morning']['end']
        afternoon_start = work_periods['afternoon']['start']
        afternoon_end = work_periods['afternoon']['end']
        infos_par_journee = {}
        df = df.sort_values(by=['date'])
        for journee, group in df.groupby(df['date'].dt.date):
            commits = list(group.sort_values(by=['date']).itertuples(index=False))
            heure_debut_journee = datetime.combine(journee, datetime.strptime(morning_start, '%H:%M').time())
            heure_fin_matin = datetime.combine(journee, datetime.strptime(morning_end, '%H:%M').time())
            heure_debut_aprem = datetime.combine(journee, datetime.strptime(afternoon_start, '%H:%M').time())
            heure_fin_journee = datetime.combine(journee, datetime.strptime(afternoon_end, '%H:%M').time())
            heure_courante = heure_debut_journee
            infos_par_journee[journee] = []
            tickets_du_jour = []
            for row in commits:
                commit_subject = getattr(row, 'message')
                commit_date = getattr(row, 'date')
                match = self.ticket_pattern.search(commit_subject)
                if not match:
                    continue
                ticket_code = match.group(0)
                if ticket_code in tickets_du_jour:
                    continue
                heure_debut = heure_courante
                heure_fin = commit_date
                erreur = False
                try:
                    if heure_debut < heure_fin_matin and heure_fin > heure_fin_matin:
                        # Première partie : matin
                        duree1 = heure_fin_matin - heure_debut
                        if duree1.total_seconds() < 0:
                            duree1 = timedelta(0)
                            erreur = True
                        duree2 = heure_fin - heure_debut_aprem
                        if duree2.total_seconds() < 0:
                            duree2 = timedelta(0)
                            erreur = True
                        infos_par_journee[journee].append({
                            'ticket': ticket_code,
                            'duree': duree1,
                            'debut': heure_debut,
                            'fin': heure_fin_matin,
                            'erreur': erreur
                        })
                        infos_par_journee[journee].append({
                            'ticket': ticket_code,
                            'duree': duree2,
                            'debut': heure_debut_aprem,
                            'fin': heure_fin,
                            'erreur': erreur
                        })
                    else:
                        duree = heure_fin - heure_debut
                        if duree.total_seconds() < 0:
                            duree = timedelta(0)
                            erreur = True
                        infos_par_journee[journee].append({
                            'ticket': ticket_code,
                            'duree': duree,
                            'debut': heure_debut,
                            'fin': heure_fin,
                            'erreur': erreur
                        })
                except Exception:
                    infos_par_journee[journee].append({
                        'ticket': ticket_code,
                        'duree': timedelta(0),
                        'debut': heure_debut,
                        'fin': heure_fin,
                        'erreur': True
                    })
                heure_courante = heure_fin
                tickets_du_jour.append(ticket_code)
            # Forcer l'heure de fin du dernier ticket à la fin de la journée
            if infos_par_journee[journee]:
                dernier = infos_par_journee[journee][-1]
                if dernier['fin'] < heure_fin_journee:
                    try:
                        duree = heure_fin_journee - dernier['debut']
                        if duree.total_seconds() < 0:
                            duree = timedelta(0)
                            dernier['erreur'] = True
                        dernier['duree'] = duree
                        dernier['fin'] = heure_fin_journee
                    except Exception:
                        dernier['duree'] = timedelta(0)
                        dernier['fin'] = heure_fin_journee
                        dernier['erreur'] = True
        return infos_par_journee
    
    def adjust_durations(self, durees_par_journee):
        """
        Ajuste les durées pour que le total par jour soit égal au nombre d'heures de travail configuré.
        
        Args:
            durees_par_journee: Un dictionnaire {jour: [tickets]} où chaque ticket est un dict.
            
        Returns:
            Un dictionnaire des durées ajustées par journée et par ticket.
        """
        work_hours = self.config.get_work_hours_per_day()
        for tickets in durees_par_journee.values():
            total_duree = sum((t['duree'] for t in tickets), timedelta())
            duree_diff = timedelta(hours=work_hours) - total_duree
            num_tickets = len(tickets)
            if num_tickets == 0:
                continue
            duree_adjust = duree_diff / num_tickets
            for t in tickets:
                t['duree'] += duree_adjust
        return durees_par_journee
    
    def filter_valid_days(self, durees_par_journee):
        """
        Filtre les jours dont le total des heures est inférieur ou égal au nombre d'heures de travail configuré.
        
        Args:
            durees_par_journee: Un dictionnaire des durées par journée et par ticket.
            
        Returns:
            Un dictionnaire filtré des durées par journée et par ticket.
        """
        work_hours = self.config.get_work_hours_per_day()
        
        return {
            journee: durees_tickets 
            for journee, durees_tickets in durees_par_journee.items() 
            if sum(durees_tickets.values(), timedelta()) <= timedelta(hours=work_hours)
        } 