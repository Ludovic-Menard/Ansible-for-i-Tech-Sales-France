#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBM i Performance Monitor - Version Python
Outil de monitoring des performances pour démonstrations commerciales IBM Power
Surveille CPU, mémoire, disque et affiche les métriques en temps réel
"""

import sys
import time
import psutil
import argparse
from datetime import datetime
from typing import Dict, List, Optional
import json


class PerformanceMonitor:
    """Classe pour monitorer les performances du système"""
    
    def __init__(self, interval: int = 5, output_file: Optional[str] = None):
        """
        Initialise le moniteur de performances
        
        Args:
            interval: Intervalle de collecte en secondes
            output_file: Fichier de sortie pour les logs (optionnel)
        """
        self.interval = interval
        self.output_file = output_file
        self.metrics_history = []
        self.start_time = datetime.now()
    
    def get_cpu_metrics(self) -> Dict:
        """
        Collecte les métriques CPU
        
        Returns:
            Dictionnaire avec les métriques CPU
        """
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_freq = psutil.cpu_freq()
        
        metrics = {
            'cpu_percent_total': psutil.cpu_percent(interval=0),
            'cpu_percent_per_core': cpu_percent,
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'cpu_count_physical': psutil.cpu_count(logical=False),
            'cpu_freq_current': cpu_freq.current if cpu_freq else 0,
            'cpu_freq_max': cpu_freq.max if cpu_freq else 0,
        }
        
        return metrics
    
    def get_memory_metrics(self) -> Dict:
        """
        Collecte les métriques mémoire
        
        Returns:
            Dictionnaire avec les métriques mémoire
        """
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        metrics = {
            'memory_total_gb': mem.total / (1024**3),
            'memory_available_gb': mem.available / (1024**3),
            'memory_used_gb': mem.used / (1024**3),
            'memory_percent': mem.percent,
            'swap_total_gb': swap.total / (1024**3),
            'swap_used_gb': swap.used / (1024**3),
            'swap_percent': swap.percent,
        }
        
        return metrics
    
    def get_disk_metrics(self) -> Dict:
        """
        Collecte les métriques disque
        
        Returns:
            Dictionnaire avec les métriques disque
        """
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        metrics = {
            'disk_total_gb': disk_usage.total / (1024**3),
            'disk_used_gb': disk_usage.used / (1024**3),
            'disk_free_gb': disk_usage.free / (1024**3),
            'disk_percent': disk_usage.percent,
            'disk_read_count': disk_io.read_count if disk_io else 0,
            'disk_write_count': disk_io.write_count if disk_io else 0,
            'disk_read_bytes': disk_io.read_bytes if disk_io else 0,
            'disk_write_bytes': disk_io.write_bytes if disk_io else 0,
        }
        
        return metrics
    
    def get_network_metrics(self) -> Dict:
        """
        Collecte les métriques réseau
        
        Returns:
            Dictionnaire avec les métriques réseau
        """
        net_io = psutil.net_io_counters()
        
        metrics = {
            'net_bytes_sent': net_io.bytes_sent,
            'net_bytes_recv': net_io.bytes_recv,
            'net_packets_sent': net_io.packets_sent,
            'net_packets_recv': net_io.packets_recv,
        }
        
        return metrics
    
    def get_process_metrics(self) -> Dict:
        """
        Collecte les métriques des processus
        
        Returns:
            Dictionnaire avec les métriques des processus
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] > 0 or pinfo['memory_percent'] > 0:
                    processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Trier par utilisation CPU
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        metrics = {
            'total_processes': len(list(psutil.process_iter())),
            'top_cpu_processes': processes[:5],  # Top 5 processus CPU
        }
        
        return metrics
    
    def collect_all_metrics(self) -> Dict:
        """
        Collecte toutes les métriques
        
        Returns:
            Dictionnaire avec toutes les métriques
        """
        timestamp = datetime.now()
        
        metrics = {
            'timestamp': timestamp.isoformat(),
            'elapsed_seconds': (timestamp - self.start_time).total_seconds(),
            'cpu': self.get_cpu_metrics(),
            'memory': self.get_memory_metrics(),
            'disk': self.get_disk_metrics(),
            'network': self.get_network_metrics(),
            'processes': self.get_process_metrics(),
        }
        
        return metrics
    
    def display_metrics(self, metrics: Dict):
        """
        Affiche les métriques dans la console
        
        Args:
            metrics: Dictionnaire des métriques
        """
        # Effacer l'écran (compatible multi-plateforme)
        print("\033[2J\033[H", end="")
        
        print("=" * 80)
        print(f"📊 MONITORING PERFORMANCES IBM i - {metrics['timestamp']}")
        print(f"⏱️  Temps écoulé: {metrics['elapsed_seconds']:.0f}s")
        print("=" * 80)
        
        # CPU
        cpu = metrics['cpu']
        print(f"\n🔥 CPU")
        print(f"   Utilisation totale:    {cpu['cpu_percent_total']:6.2f}%")
        print(f"   Cœurs logiques:        {cpu['cpu_count_logical']}")
        print(f"   Cœurs physiques:       {cpu['cpu_count_physical']}")
        if cpu['cpu_freq_current'] > 0:
            print(f"   Fréquence actuelle:    {cpu['cpu_freq_current']:.0f} MHz")
        
        # Afficher l'utilisation par cœur
        print(f"\n   Utilisation par cœur:")
        for i, percent in enumerate(cpu['cpu_percent_per_core']):
            bar_length = int(percent / 2)  # Barre de 50 caractères max
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"   Core {i:2d}: [{bar}] {percent:6.2f}%")
        
        # Mémoire
        mem = metrics['memory']
        print(f"\n💾 MÉMOIRE")
        print(f"   Total:                 {mem['memory_total_gb']:6.2f} GB")
        print(f"   Utilisée:              {mem['memory_used_gb']:6.2f} GB ({mem['memory_percent']:.1f}%)")
        print(f"   Disponible:            {mem['memory_available_gb']:6.2f} GB")
        
        mem_bar_length = int(mem['memory_percent'] / 2)
        mem_bar = "█" * mem_bar_length + "░" * (50 - mem_bar_length)
        print(f"   [{mem_bar}] {mem['memory_percent']:.1f}%")
        
        if mem['swap_total_gb'] > 0:
            print(f"\n   Swap Total:            {mem['swap_total_gb']:6.2f} GB")
            print(f"   Swap Utilisé:          {mem['swap_used_gb']:6.2f} GB ({mem['swap_percent']:.1f}%)")
        
        # Disque
        disk = metrics['disk']
        print(f"\n💿 DISQUE")
        print(f"   Total:                 {disk['disk_total_gb']:6.2f} GB")
        print(f"   Utilisé:               {disk['disk_used_gb']:6.2f} GB ({disk['disk_percent']:.1f}%)")
        print(f"   Libre:                 {disk['disk_free_gb']:6.2f} GB")
        
        disk_bar_length = int(disk['disk_percent'] / 2)
        disk_bar = "█" * disk_bar_length + "░" * (50 - disk_bar_length)
        print(f"   [{disk_bar}] {disk['disk_percent']:.1f}%")
        
        print(f"\n   Lectures:              {disk['disk_read_count']:,}")
        print(f"   Écritures:             {disk['disk_write_count']:,}")
        print(f"   Données lues:          {disk['disk_read_bytes'] / (1024**3):6.2f} GB")
        print(f"   Données écrites:       {disk['disk_write_bytes'] / (1024**3):6.2f} GB")
        
        # Réseau
        net = metrics['network']
        print(f"\n🌐 RÉSEAU")
        print(f"   Données envoyées:      {net['net_bytes_sent'] / (1024**3):6.2f} GB")
        print(f"   Données reçues:        {net['net_bytes_recv'] / (1024**3):6.2f} GB")
        print(f"   Paquets envoyés:       {net['net_packets_sent']:,}")
        print(f"   Paquets reçus:         {net['net_packets_recv']:,}")
        
        # Processus
        proc = metrics['processes']
        print(f"\n⚙️  PROCESSUS")
        print(f"   Total:                 {proc['total_processes']}")
        print(f"\n   Top 5 CPU:")
        for i, p in enumerate(proc['top_cpu_processes'][:5], 1):
            print(f"   {i}. {p['name'][:30]:30s} - CPU: {p['cpu_percent']:5.1f}% - MEM: {p['memory_percent']:5.1f}%")
        
        print("\n" + "=" * 80)
        print(f"Prochain rafraîchissement dans {self.interval} secondes... (Ctrl+C pour arrêter)")
    
    def save_metrics(self, metrics: Dict):
        """
        Sauvegarde les métriques dans un fichier
        
        Args:
            metrics: Dictionnaire des métriques
        """
        if self.output_file:
            try:
                with open(self.output_file, 'a') as f:
                    f.write(json.dumps(metrics) + '\n')
            except Exception as e:
                print(f"⚠️  Erreur lors de la sauvegarde: {e}")
    
    def run(self, duration: Optional[int] = None):
        """
        Lance le monitoring
        
        Args:
            duration: Durée du monitoring en secondes (None = infini)
        """
        print(f"🚀 Démarrage du monitoring des performances")
        print(f"   Intervalle: {self.interval} secondes")
        if duration:
            print(f"   Durée: {duration} secondes")
        else:
            print(f"   Durée: Infinie (Ctrl+C pour arrêter)")
        if self.output_file:
            print(f"   Fichier de sortie: {self.output_file}")
        print("\n")
        
        start_time = time.time()
        
        try:
            while True:
                # Collecter les métriques
                metrics = self.collect_all_metrics()
                self.metrics_history.append(metrics)
                
                # Afficher les métriques
                self.display_metrics(metrics)
                
                # Sauvegarder si nécessaire
                self.save_metrics(metrics)
                
                # Vérifier la durée
                if duration and (time.time() - start_time) >= duration:
                    break
                
                # Attendre l'intervalle
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Monitoring interrompu par l'utilisateur")
        
        # Afficher le résumé
        self.display_summary()
    
    def display_summary(self):
        """Affiche un résumé des métriques collectées"""
        if not self.metrics_history:
            return
        
        print("\n" + "=" * 80)
        print("📈 RÉSUMÉ DU MONITORING")
        print("=" * 80)
        
        # Calculer les moyennes
        avg_cpu = sum(m['cpu']['cpu_percent_total'] for m in self.metrics_history) / len(self.metrics_history)
        avg_mem = sum(m['memory']['memory_percent'] for m in self.metrics_history) / len(self.metrics_history)
        avg_disk = sum(m['disk']['disk_percent'] for m in self.metrics_history) / len(self.metrics_history)
        
        max_cpu = max(m['cpu']['cpu_percent_total'] for m in self.metrics_history)
        max_mem = max(m['memory']['memory_percent'] for m in self.metrics_history)
        
        print(f"Durée totale:           {self.metrics_history[-1]['elapsed_seconds']:.0f} secondes")
        print(f"Échantillons collectés: {len(self.metrics_history)}")
        print(f"\nCPU moyen:              {avg_cpu:.2f}%")
        print(f"CPU maximum:            {max_cpu:.2f}%")
        print(f"\nMémoire moyenne:        {avg_mem:.2f}%")
        print(f"Mémoire maximum:        {max_mem:.2f}%")
        print(f"\nDisque moyen:           {avg_disk:.2f}%")
        
        if self.output_file:
            print(f"\n✅ Métriques sauvegardées dans: {self.output_file}")
        
        print("=" * 80)


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='Outil de monitoring des performances pour IBM i',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  # Monitoring continu avec rafraîchissement toutes les 5 secondes
  python ibmi_monitor.py
  
  # Monitoring pendant 5 minutes avec intervalle de 2 secondes
  python ibmi_monitor.py --duration 300 --interval 2
  
  # Monitoring avec sauvegarde dans un fichier
  python ibmi_monitor.py --output metrics.jsonl --duration 600
  
  # Monitoring rapide (1 seconde) pendant 2 minutes
  python ibmi_monitor.py --interval 1 --duration 120
        """
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Intervalle de collecte en secondes (défaut: 5)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=None,
        help='Durée du monitoring en secondes (défaut: infini)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Fichier de sortie pour les métriques (format JSON Lines)'
    )
    
    args = parser.parse_args()
    
    # Valider les paramètres
    if args.interval <= 0:
        print("❌ Erreur: L'intervalle doit être supérieur à 0")
        sys.exit(1)
    
    if args.duration and args.duration <= 0:
        print("❌ Erreur: La durée doit être supérieure à 0")
        sys.exit(1)
    
    # Lancer le monitoring
    try:
        monitor = PerformanceMonitor(args.interval, args.output)
        monitor.run(args.duration)
        
        print("\n✅ Monitoring terminé avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du monitoring: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

# Made with Bob
