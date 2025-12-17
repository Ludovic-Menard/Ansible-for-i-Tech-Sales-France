#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBM i CPU Stress Test with SMT Control - Version Python
Outil de stress test CPU avec contrôle SMT pour démonstrations commerciales IBM Power
Génère une charge intensive CPU avec options SMT 1, 2, 4 ou 8
"""

import os
import sys
import time
import math
import argparse
import multiprocessing
from datetime import datetime, timedelta
from typing import Optional


class CPUStressTestSMT:
    """Classe pour effectuer des tests de stress CPU sur IBM i avec contrôle SMT"""
    
    def __init__(self, duration: int, intensity: str = 'high', smt_mode: int = 8):
        """
        Initialise le test de stress CPU avec contrôle SMT
        
        Args:
            duration: Durée du test en secondes
            intensity: Intensité du test ('low', 'medium', 'high', 'extreme')
            smt_mode: Mode SMT (1, 2, 4, ou 8)
        """
        self.duration = duration
        self.intensity = intensity
        self.smt_mode = smt_mode
        self.iterations = 0
        self.result = 0.0
        
        # Définir le nombre d'itérations selon l'intensité
        self.intensity_levels = {
            'low': 100000,
            'medium': 500000,
            'high': 1000000,
            'extreme': 5000000
        }
        self.max_calc = self.intensity_levels.get(intensity, 1000000)
    
    def set_cpu_affinity(self, worker_id: int):
        """
        Configure l'affinité CPU selon le mode SMT
        
        Args:
            worker_id: Identifiant du worker
            
        Returns:
            ID du CPU assigné ou None
        """
        try:
            # Obtenir le nombre de CPUs disponibles
            total_cpus = multiprocessing.cpu_count()
            
            # Calculer les CPUs à utiliser selon le mode SMT
            # SMT 1: 1 thread par core physique
            # SMT 2: 2 threads par core physique
            # SMT 4: 4 threads par core physique
            # SMT 8: 8 threads par core physique (tous les threads)
            
            if self.smt_mode == 1:
                # Utiliser seulement les CPUs primaires (0, 8, 16, 24...)
                cpu_list = list(range(0, total_cpus, 8))
            elif self.smt_mode == 2:
                # Utiliser les CPUs par paires (0-1, 8-9, 16-17...)
                cpu_list = []
                for i in range(0, total_cpus, 8):
                    cpu_list.extend([i, i+1])
            elif self.smt_mode == 4:
                # Utiliser 4 threads par core (0-3, 8-11, 16-19...)
                cpu_list = []
                for i in range(0, total_cpus, 8):
                    cpu_list.extend([i, i+1, i+2, i+3])
            else:  # SMT 8
                # Utiliser tous les CPUs
                cpu_list = list(range(total_cpus))
            
            # Assigner le CPU au worker
            if cpu_list:
                cpu_id = cpu_list[worker_id % len(cpu_list)]
                os.sched_setaffinity(0, {cpu_id})
                print(f"   🔧 Worker {worker_id} assigné au CPU {cpu_id} (SMT {self.smt_mode})")
                return cpu_id
            
        except Exception as e:
            print(f"   ⚠️  Impossible de définir l'affinité CPU: {e}")
            return None
    
    def calculate_intensive(self, i: int) -> float:
        """
        Effectue des calculs mathématiques intensifs
        
        Args:
            i: Valeur d'itération
            
        Returns:
            Résultat du calcul
        """
        result = 0.0
        
        # Opérations mathématiques intensives
        result = math.sqrt(i * 3.14159)
        result = result * result
        result = math.sqrt(result) + math.sqrt(i)
        
        # Calculs trigonométriques
        for j in range(1, 101):
            result += (j * 1.732) / (i + 1)
            result -= (j * 0.577) * (i + 1)
        
        # Opérations de division
        if i > 0:
            result = result / i
            result = result * i
        
        return result
    
    def run_stress_loop(self, worker_id: int = 0) -> dict:
        """
        Exécute la boucle principale de stress CPU
        
        Args:
            worker_id: Identifiant du worker
            
        Returns:
            Dictionnaire avec les statistiques du test
        """
        # Configurer l'affinité CPU
        cpu_id = self.set_cpu_affinity(worker_id)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=self.duration)
        
        print(f"🚀 Démarrage du test de stress CPU (Worker {worker_id})")
        print(f"   Durée: {self.duration} secondes")
        print(f"   Intensité: {self.intensity}")
        print(f"   Mode SMT: {self.smt_mode}")
        if cpu_id is not None:
            print(f"   CPU assigné: {cpu_id}")
        print(f"   Début: {start_time.strftime('%H:%M:%S')}")
        print(f"   Fin prévue: {end_time.strftime('%H:%M:%S')}")
        print("-" * 60)
        
        # Boucle principale de stress
        last_progress_time = 0
        while datetime.now() < end_time:
            # Première série de calculs
            for i in range(1, self.max_calc + 1):
                self.result = self.calculate_intensive(i)
                self.iterations += 1
                
                # Vérifier le temps périodiquement
                if i % 10000 == 0:
                    if datetime.now() >= end_time:
                        break
            
            # Boucles imbriquées supplémentaires pour plus de stress
            for j in range(1, 1001):
                for k in range(1, 101):
                    self.result = math.sqrt(j * k) + (j / (k + 1))
            
            # Afficher la progression toutes les 10 secondes
            elapsed = (datetime.now() - start_time).total_seconds()
            if int(elapsed) % 10 == 0 and int(elapsed) != last_progress_time and elapsed > 0:
                progress = (elapsed / self.duration) * 100
                print(f"⏱️  Worker {worker_id} - Progression: {progress:.1f}% - Itérations: {self.iterations:,}")
                last_progress_time = int(elapsed)
        
        # Calculer les statistiques finales
        actual_end = datetime.now()
        elapsed_seconds = (actual_end - start_time).total_seconds()
        
        stats = {
            'start_time': start_time,
            'end_time': actual_end,
            'elapsed_seconds': elapsed_seconds,
            'iterations': self.iterations,
            'final_result': self.result,
            'iterations_per_second': self.iterations / elapsed_seconds if elapsed_seconds > 0 else 0,
            'smt_mode': self.smt_mode,
            'cpu_id': cpu_id
        }
        
        return stats
    
    def display_results(self, stats: dict):
        """
        Affiche les résultats du test
        
        Args:
            stats: Dictionnaire des statistiques
        """
        print("\n" + "=" * 60)
        print("✅ TEST DE STRESS CPU TERMINÉ")
        print("=" * 60)
        print(f"Mode SMT:             {stats['smt_mode']}")
        if stats.get('cpu_id') is not None:
            print(f"CPU utilisé:          {stats['cpu_id']}")
        print(f"Début:                {stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Fin:                  {stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Durée réelle:         {stats['elapsed_seconds']:.2f} secondes")
        print(f"Itérations totales:   {stats['iterations']:,}")
        print(f"Itérations/seconde:   {stats['iterations_per_second']:,.0f}")
        print(f"Résultat final:       {stats['final_result']:.6f}")
        print("=" * 60)


def worker_process(duration: int, intensity: str, smt_mode: int, worker_id: int):
    """
    Fonction exécutée par chaque processus worker
    
    Args:
        duration: Durée du test
        intensity: Intensité du test
        smt_mode: Mode SMT
        worker_id: Identifiant du worker
    """
    print(f"\n🔧 Worker {worker_id} démarré (PID: {multiprocessing.current_process().pid})")
    
    stress_test = CPUStressTestSMT(duration, intensity, smt_mode)
    stats = stress_test.run_stress_loop(worker_id)
    
    print(f"\n✅ Worker {worker_id} terminé")
    print(f"   Itérations: {stats['iterations']:,}")
    print(f"   Durée: {stats['elapsed_seconds']:.2f}s")
    if stats.get('cpu_id') is not None:
        print(f"   CPU: {stats['cpu_id']}")
    
    return stats


def run_multi_core_stress(duration: int, num_cores: int, intensity: str = 'high', smt_mode: int = 8):
    """
    Lance un test de stress sur plusieurs cœurs CPU avec contrôle SMT
    
    Args:
        duration: Durée du test en secondes
        num_cores: Nombre de cœurs à stresser
        intensity: Intensité du test
        smt_mode: Mode SMT
    """
    print("\n" + "=" * 60)
    print("🎯 TEST DE STRESS MULTI-CŒURS AVEC CONTRÔLE SMT")
    print("=" * 60)
    print(f"Mode SMT:          {smt_mode}")
    print(f"Nombre de workers: {num_cores}")
    print(f"Durée par worker:  {duration} secondes")
    print(f"Intensité:         {intensity}")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # Créer un pool de processus
    with multiprocessing.Pool(processes=num_cores) as pool:
        # Lancer les workers en parallèle
        results = []
        for i in range(num_cores):
            result = pool.apply_async(worker_process, (duration, intensity, smt_mode, i + 1))
            results.append(result)
        
        # Attendre que tous les workers se terminent
        all_stats = [r.get() for r in results]
    
    end_time = datetime.now()
    total_elapsed = (end_time - start_time).total_seconds()
    
    # Calculer les statistiques globales
    total_iterations = sum(s['iterations'] for s in all_stats)
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS GLOBAUX")
    print("=" * 60)
    print(f"Mode SMT:               {smt_mode}")
    print(f"Durée totale:           {total_elapsed:.2f} secondes")
    print(f"Workers utilisés:       {num_cores}")
    print(f"Itérations totales:     {total_iterations:,}")
    print(f"Itérations/seconde:     {total_iterations / total_elapsed:,.0f}")
    print(f"Charge CPU estimée:     {num_cores * 100}% (théorique)")
    print("=" * 60)


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='Outil de stress test CPU avec contrôle SMT pour IBM i - Démonstrations commerciales',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  # Test simple sur 1 cœur pendant 60 secondes en SMT 1
  python ibmi_stress_cpu_smt.py --duration 60 --smt 1
  
  # Test sur 4 cœurs pendant 5 minutes en SMT 2
  python ibmi_stress_cpu_smt.py --duration 300 --cores 4 --smt 2
  
  # Test intensif sur 8 cœurs pendant 10 minutes en SMT 4
  python ibmi_stress_cpu_smt.py --duration 600 --cores 8 --intensity extreme --smt 4
  
  # Test léger pour démonstration en SMT 8 (défaut)
  python ibmi_stress_cpu_smt.py --duration 30 --cores 2 --intensity low --smt 8

Modes SMT:
  SMT 1: 1 thread par core physique (performance maximale par thread)
  SMT 2: 2 threads par core physique (équilibre performance/parallélisme)
  SMT 4: 4 threads par core physique (parallélisme élevé)
  SMT 8: 8 threads par core physique (parallélisme maximal, défaut IBM i)
        """
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        required=True,
        help='Durée du test en secondes'
    )
    
    parser.add_argument(
        '--cores',
        type=int,
        default=1,
        help='Nombre de cœurs CPU à stresser (défaut: 1)'
    )
    
    parser.add_argument(
        '--intensity',
        choices=['low', 'medium', 'high', 'extreme'],
        default='high',
        help='Intensité du test (défaut: high)'
    )
    
    parser.add_argument(
        '--smt',
        type=int,
        choices=[1, 2, 4, 8],
        default=8,
        help='Mode SMT: 1, 2, 4 ou 8 threads par core (défaut: 8)'
    )
    
    args = parser.parse_args()
    
    # Valider les paramètres
    if args.duration <= 0:
        print("❌ Erreur: La durée doit être supérieure à 0")
        sys.exit(1)
    
    if args.cores <= 0:
        print("❌ Erreur: Le nombre de cœurs doit être supérieur à 0")
        sys.exit(1)
    
    max_cores = multiprocessing.cpu_count()
    if args.cores > max_cores:
        print(f"⚠️  Attention: {args.cores} cœurs demandés, mais seulement {max_cores} disponibles")
        print(f"   Utilisation de {max_cores} cœurs")
        args.cores = max_cores
    
    # Afficher les informations système
    print("\n" + "=" * 60)
    print("🖥️  INFORMATIONS SYSTÈME")
    print("=" * 60)
    print(f"CPUs disponibles:     {multiprocessing.cpu_count()}")
    print(f"Mode SMT configuré:   {args.smt}")
    print("=" * 60)
    
    # Lancer le test
    try:
        if args.cores == 1:
            # Test sur un seul cœur
            stress_test = CPUStressTestSMT(args.duration, args.intensity, args.smt)
            stats = stress_test.run_stress_loop(1)
            stress_test.display_results(stats)
        else:
            # Test multi-cœurs
            run_multi_core_stress(args.duration, args.cores, args.intensity, args.smt)
        
        print("\n✅ Test CPU avec contrôle SMT terminé avec succès!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

# Made with Bob