#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBM i Stress Test Orchestrator - Version Python
Orchestrateur pour lancer et gérer plusieurs tests de stress simultanés
Idéal pour les démonstrations commerciales IBM Power
"""

import sys
import time
import subprocess
import argparse
import signal
from datetime import datetime
from typing import List, Dict, Optional
import json


class StressTestOrchestrator:
    """Classe pour orchestrer plusieurs tests de stress"""
    
    def __init__(self):
        """Initialise l'orchestrateur"""
        self.processes = []
        self.test_results = []
        self.start_time = None
        self.monitor_process = None
    
    def start_cpu_stress(self, duration: int, cores: int, intensity: str = 'high') -> subprocess.Popen:
        """
        Lance un test de stress CPU
        
        Args:
            duration: Durée du test en secondes
            cores: Nombre de cœurs à stresser
            intensity: Intensité du test
            
        Returns:
            Processus lancé
        """
        cmd = [
            sys.executable,
            'ibmi_stress_cpu.py',
            '--duration', str(duration),
            '--cores', str(cores),
            '--intensity', intensity
        ]
        
        print(f"🚀 Lancement du stress CPU: {cores} cœurs, {duration}s, intensité {intensity}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        return process
    
    def start_io_stress(self, duration: int, processes: int, directory: str,
                       file_size: int = 100, operation: str = 'mixed') -> subprocess.Popen:
        """
        Lance un test de stress I/O
        
        Args:
            duration: Durée du test en secondes
            processes: Nombre de processus
            directory: Répertoire de test
            file_size: Taille des fichiers en MB
            operation: Type d'opération
            
        Returns:
            Processus lancé
        """
        cmd = [
            sys.executable,
            'ibmi_stress_io.py',
            '--duration', str(duration),
            '--processes', str(processes),
            '--directory', directory,
            '--file-size', str(file_size),
            '--operation', operation,
            '--cleanup'
        ]
        
        print(f"🚀 Lancement du stress I/O: {processes} processus, {duration}s, {operation}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        return process
    
    def start_monitor(self, interval: int = 5, output_file: Optional[str] = None) -> subprocess.Popen:
        """
        Lance le monitoring des performances
        
        Args:
            interval: Intervalle de collecte
            output_file: Fichier de sortie
            
        Returns:
            Processus lancé
        """
        cmd = [
            sys.executable,
            'ibmi_monitor.py',
            '--interval', str(interval)
        ]
        
        if output_file:
            cmd.extend(['--output', output_file])
        
        print(f"📊 Lancement du monitoring (intervalle: {interval}s)")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        return process
    
    def wait_for_processes(self, processes: List[subprocess.Popen], timeout: Optional[int] = None):
        """
        Attend la fin de tous les processus
        
        Args:
            processes: Liste des processus
            timeout: Timeout en secondes
        """
        print(f"\n⏳ Attente de la fin des {len(processes)} processus...")
        
        for i, process in enumerate(processes, 1):
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                
                if process.returncode == 0:
                    print(f"✅ Processus {i}/{len(processes)} terminé avec succès")
                else:
                    print(f"⚠️  Processus {i}/{len(processes)} terminé avec erreur (code: {process.returncode})")
                
                # Sauvegarder les résultats
                self.test_results.append({
                    'process_id': i,
                    'return_code': process.returncode,
                    'stdout': stdout,
                    'stderr': stderr
                })
                
            except subprocess.TimeoutExpired:
                print(f"⚠️  Timeout pour le processus {i}/{len(processes)}")
                process.kill()
    
    def stop_all_processes(self):
        """Arrête tous les processus en cours"""
        print("\n🛑 Arrêt de tous les processus...")
        
        for process in self.processes:
            if process.poll() is None:  # Processus encore en cours
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        if self.monitor_process and self.monitor_process.poll() is None:
            self.monitor_process.terminate()
            try:
                self.monitor_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.monitor_process.kill()
        
        print("✅ Tous les processus arrêtés")
    
    def run_scenario(self, scenario: Dict):
        """
        Exécute un scénario de test
        
        Args:
            scenario: Configuration du scénario
        """
        print("\n" + "=" * 80)
        print(f"🎯 SCÉNARIO: {scenario['name']}")
        print("=" * 80)
        print(f"Description: {scenario['description']}")
        print(f"Durée: {scenario['duration']} secondes")
        print("=" * 80 + "\n")
        
        self.start_time = datetime.now()
        self.processes = []
        
        # Démarrer le monitoring si demandé
        if scenario.get('monitor', True):
            monitor_output = f"metrics_{scenario['name'].replace(' ', '_')}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.jsonl"
            self.monitor_process = self.start_monitor(
                interval=scenario.get('monitor_interval', 5),
                output_file=monitor_output
            )
            time.sleep(2)  # Laisser le monitoring démarrer
        
        # Lancer les tests CPU
        if 'cpu_tests' in scenario:
            for cpu_test in scenario['cpu_tests']:
                process = self.start_cpu_stress(
                    duration=scenario['duration'],
                    cores=cpu_test.get('cores', 1),
                    intensity=cpu_test.get('intensity', 'high')
                )
                self.processes.append(process)
                time.sleep(1)  # Petit délai entre les lancements
        
        # Lancer les tests I/O
        if 'io_tests' in scenario:
            for io_test in scenario['io_tests']:
                process = self.start_io_stress(
                    duration=scenario['duration'],
                    processes=io_test.get('processes', 1),
                    directory=io_test.get('directory', '/tmp/ibmi_io_stress'),
                    file_size=io_test.get('file_size', 100),
                    operation=io_test.get('operation', 'mixed')
                )
                self.processes.append(process)
                time.sleep(1)
        
        # Attendre la fin des tests
        self.wait_for_processes(self.processes, timeout=scenario['duration'] + 60)
        
        # Arrêter le monitoring
        if self.monitor_process:
            time.sleep(2)  # Laisser le monitoring collecter les dernières métriques
            self.monitor_process.terminate()
            try:
                self.monitor_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.monitor_process.kill()
        
        # Afficher le résumé
        self.display_summary(scenario)
    
    def display_summary(self, scenario: Dict):
        """
        Affiche le résumé du scénario
        
        Args:
            scenario: Configuration du scénario
        """
        if not self.start_time:
            return
        
        end_time = datetime.now()
        elapsed = (end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DU SCÉNARIO")
        print("=" * 80)
        print(f"Scénario:             {scenario['name']}")
        print(f"Début:                {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Fin:                  {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Durée totale:         {elapsed:.0f} secondes")
        print(f"Processus lancés:     {len(self.processes)}")
        
        # Compter les succès et échecs
        success_count = sum(1 for r in self.test_results if r['return_code'] == 0)
        error_count = len(self.test_results) - success_count
        
        print(f"Tests réussis:        {success_count}")
        print(f"Tests en erreur:      {error_count}")
        print("=" * 80)


def load_scenario_from_file(filename: str) -> Dict:
    """
    Charge un scénario depuis un fichier JSON
    
    Args:
        filename: Nom du fichier
        
    Returns:
        Configuration du scénario
    """
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erreur lors du chargement du scénario: {e}")
        sys.exit(1)


def get_predefined_scenarios() -> Dict[str, Dict]:
    """
    Retourne les scénarios prédéfinis
    
    Returns:
        Dictionnaire des scénarios
    """
    return {
        'demo_light': {
            'name': 'Démonstration Légère',
            'description': 'Test léger pour démonstration rapide (2 minutes)',
            'duration': 120,
            'monitor': True,
            'monitor_interval': 5,
            'cpu_tests': [
                {'cores': 2, 'intensity': 'medium'}
            ],
            'io_tests': [
                {'processes': 1, 'file_size': 50, 'operation': 'mixed'}
            ]
        },
        'demo_standard': {
            'name': 'Démonstration Standard',
            'description': 'Test standard pour démonstration client (5 minutes)',
            'duration': 300,
            'monitor': True,
            'monitor_interval': 5,
            'cpu_tests': [
                {'cores': 4, 'intensity': 'high'}
            ],
            'io_tests': [
                {'processes': 2, 'file_size': 100, 'operation': 'mixed'}
            ]
        },
        'demo_intensive': {
            'name': 'Démonstration Intensive',
            'description': 'Test intensif pour montrer les capacités (10 minutes)',
            'duration': 600,
            'monitor': True,
            'monitor_interval': 3,
            'cpu_tests': [
                {'cores': 8, 'intensity': 'extreme'}
            ],
            'io_tests': [
                {'processes': 4, 'file_size': 200, 'operation': 'mixed'}
            ]
        },
        'cpu_only': {
            'name': 'Stress CPU Uniquement',
            'description': 'Test de stress CPU pur (5 minutes)',
            'duration': 300,
            'monitor': True,
            'monitor_interval': 5,
            'cpu_tests': [
                {'cores': 4, 'intensity': 'high'},
                {'cores': 4, 'intensity': 'high'}
            ]
        },
        'io_only': {
            'name': 'Stress I/O Uniquement',
            'description': 'Test de stress I/O pur (5 minutes)',
            'duration': 300,
            'monitor': True,
            'monitor_interval': 5,
            'io_tests': [
                {'processes': 4, 'file_size': 200, 'operation': 'write'},
                {'processes': 4, 'file_size': 200, 'operation': 'read'}
            ]
        },
        'full_stress': {
            'name': 'Stress Complet',
            'description': 'Test de stress complet CPU + I/O (15 minutes)',
            'duration': 900,
            'monitor': True,
            'monitor_interval': 5,
            'cpu_tests': [
                {'cores': 8, 'intensity': 'extreme'}
            ],
            'io_tests': [
                {'processes': 4, 'file_size': 200, 'operation': 'mixed'},
                {'processes': 4, 'file_size': 200, 'operation': 'write'}
            ]
        }
    }


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='Orchestrateur de tests de stress pour IBM i - Démonstrations commerciales',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Scénarios prédéfinis disponibles:
  demo_light      - Démonstration légère (2 min)
  demo_standard   - Démonstration standard (5 min)
  demo_intensive  - Démonstration intensive (10 min)
  cpu_only        - Stress CPU uniquement (5 min)
  io_only         - Stress I/O uniquement (5 min)
  full_stress     - Stress complet CPU + I/O (15 min)

Exemples d'utilisation:
  # Lancer un scénario prédéfini
  python ibmi_stress_orchestrator.py --scenario demo_standard
  
  # Lancer un scénario depuis un fichier JSON
  python ibmi_stress_orchestrator.py --file my_scenario.json
  
  # Lister les scénarios disponibles
  python ibmi_stress_orchestrator.py --list-scenarios
        """
    )
    
    parser.add_argument(
        '--scenario',
        type=str,
        help='Nom du scénario prédéfini à exécuter'
    )
    
    parser.add_argument(
        '--file',
        type=str,
        help='Fichier JSON contenant la configuration du scénario'
    )
    
    parser.add_argument(
        '--list-scenarios',
        action='store_true',
        help='Afficher la liste des scénarios prédéfinis'
    )
    
    args = parser.parse_args()
    
    # Afficher la liste des scénarios
    if args.list_scenarios:
        scenarios = get_predefined_scenarios()
        print("\n" + "=" * 80)
        print("📋 SCÉNARIOS PRÉDÉFINIS DISPONIBLES")
        print("=" * 80)
        for key, scenario in scenarios.items():
            print(f"\n🎯 {key}")
            print(f"   Nom:         {scenario['name']}")
            print(f"   Description: {scenario['description']}")
            print(f"   Durée:       {scenario['duration']} secondes")
        print("\n" + "=" * 80)
        return
    
    # Charger le scénario
    scenario = None
    if args.scenario:
        scenarios = get_predefined_scenarios()
        if args.scenario not in scenarios:
            print(f"❌ Erreur: Scénario '{args.scenario}' inconnu")
            print(f"   Utilisez --list-scenarios pour voir les scénarios disponibles")
            sys.exit(1)
        scenario = scenarios[args.scenario]
    elif args.file:
        scenario = load_scenario_from_file(args.file)
    else:
        print("❌ Erreur: Vous devez spécifier --scenario ou --file")
        parser.print_help()
        sys.exit(1)
    
    # Créer l'orchestrateur
    orchestrator = StressTestOrchestrator()
    
    # Gérer l'interruption (Ctrl+C)
    def signal_handler(sig, frame):
        print("\n\n⚠️  Interruption détectée...")
        orchestrator.stop_all_processes()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Lancer le scénario
    try:
        orchestrator.run_scenario(scenario)
        print("\n✅ Scénario terminé avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution du scénario: {e}")
        import traceback
        traceback.print_exc()
        orchestrator.stop_all_processes()
        sys.exit(1)


if __name__ == '__main__':
    main()

# Made with Bob
