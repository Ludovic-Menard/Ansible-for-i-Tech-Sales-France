#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBM i I/O Stress Test with SMT Control - Version Python
Outil de stress test I/O disque avec contrôle SMT pour démonstrations commerciales IBM Power
Génère une charge intensive sur les disques avec options SMT 1, 2, 4 ou 8
"""

import os
import sys
import time
import random
import argparse
import multiprocessing
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import subprocess


class IOStressTestSMT:
    """Classe pour effectuer des tests de stress I/O sur IBM i avec contrôle SMT"""
    
    def __init__(self, duration: int, directory: str, file_size_mb: int = 100, 
                 operation: str = 'mixed', smt_mode: int = 8):
        """
        Initialise le test de stress I/O avec contrôle SMT
        
        Args:
            duration: Durée du test en secondes
            directory: Répertoire pour les fichiers de test
            file_size_mb: Taille des fichiers en MB
            operation: Type d'opération ('read', 'write', 'mixed')
            smt_mode: Mode SMT (1, 2, 4, ou 8)
        """
        self.duration = duration
        self.directory = Path(directory)
        self.file_size_mb = file_size_mb
        self.operation = operation
        self.smt_mode = smt_mode
        self.bytes_written = 0
        self.bytes_read = 0
        self.files_created = 0
        self.operations_count = 0
        
        # Créer le répertoire s'il n'existe pas
        self.directory.mkdir(parents=True, exist_ok=True)
    
    def set_cpu_affinity(self, worker_id: int):
        """
        Configure l'affinité CPU selon le mode SMT
        
        Args:
            worker_id: Identifiant du worker
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
    
    def get_smt_info(self):
        """Récupère les informations SMT du système"""
        try:
            # Essayer de lire les informations SMT depuis /proc/cpuinfo
            with open('/proc/cpuinfo', 'r') as f:
                content = f.read()
                # Compter les processeurs
                processors = content.count('processor')
                return processors
        except:
            return multiprocessing.cpu_count()
    
    def generate_random_data(self, size_bytes: int) -> bytes:
        """
        Génère des données aléatoires
        
        Args:
            size_bytes: Taille des données en bytes
            
        Returns:
            Données aléatoires
        """
        return os.urandom(size_bytes)
    
    def write_file(self, file_path: Path, size_mb: int) -> int:
        """
        Écrit un fichier avec des données aléatoires
        
        Args:
            file_path: Chemin du fichier
            size_mb: Taille en MB
            
        Returns:
            Nombre de bytes écrits
        """
        chunk_size = 1024 * 1024  # 1 MB chunks
        bytes_written = 0
        
        with open(file_path, 'wb') as f:
            for _ in range(size_mb):
                data = self.generate_random_data(chunk_size)
                f.write(data)
                bytes_written += len(data)
                f.flush()
                os.fsync(f.fileno())  # Force l'écriture sur disque
        
        return bytes_written
    
    def read_file(self, file_path: Path) -> int:
        """
        Lit un fichier complètement
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            Nombre de bytes lus
        """
        chunk_size = 1024 * 1024  # 1 MB chunks
        bytes_read = 0
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                bytes_read += len(chunk)
        
        return bytes_read
    
    def perform_write_operations(self, end_time: datetime):
        """
        Effectue des opérations d'écriture
        
        Args:
            end_time: Heure de fin du test
        """
        file_counter = 0
        
        while datetime.now() < end_time:
            file_path = self.directory / f"stress_write_{file_counter}.dat"
            
            try:
                bytes_written = self.write_file(file_path, self.file_size_mb)
                self.bytes_written += bytes_written
                self.files_created += 1
                self.operations_count += 1
                file_counter += 1
                
                # Afficher la progression
                if file_counter % 10 == 0:
                    print(f"   📝 Fichiers écrits: {file_counter} ({self.bytes_written / (1024**3):.2f} GB)")
                
            except Exception as e:
                print(f"❌ Erreur d'écriture: {e}")
                break
    
    def perform_read_operations(self, end_time: datetime):
        """
        Effectue des opérations de lecture
        
        Args:
            end_time: Heure de fin du test
        """
        # Créer quelques fichiers pour la lecture
        print("   📝 Création de fichiers de test pour la lecture...")
        test_files = []
        for i in range(10):
            file_path = self.directory / f"stress_read_{i}.dat"
            self.write_file(file_path, self.file_size_mb)
            test_files.append(file_path)
        
        print(f"   ✅ {len(test_files)} fichiers créés")
        
        # Lire les fichiers en boucle
        read_counter = 0
        while datetime.now() < end_time:
            file_path = random.choice(test_files)
            
            try:
                bytes_read = self.read_file(file_path)
                self.bytes_read += bytes_read
                self.operations_count += 1
                read_counter += 1
                
                # Afficher la progression
                if read_counter % 50 == 0:
                    print(f"   📖 Lectures effectuées: {read_counter} ({self.bytes_read / (1024**3):.2f} GB)")
                
            except Exception as e:
                print(f"❌ Erreur de lecture: {e}")
                break
    
    def perform_mixed_operations(self, end_time: datetime):
        """
        Effectue des opérations mixtes (lecture et écriture)
        
        Args:
            end_time: Heure de fin du test
        """
        # Créer quelques fichiers initiaux
        print("   📝 Création de fichiers initiaux...")
        test_files = []
        for i in range(5):
            file_path = self.directory / f"stress_mixed_{i}.dat"
            self.write_file(file_path, self.file_size_mb)
            test_files.append(file_path)
        
        print(f"   ✅ {len(test_files)} fichiers créés")
        
        file_counter = len(test_files)
        operation_counter = 0
        
        while datetime.now() < end_time:
            # Alterner entre lecture et écriture
            if random.random() < 0.5:  # 50% écriture
                file_path = self.directory / f"stress_mixed_{file_counter}.dat"
                try:
                    bytes_written = self.write_file(file_path, self.file_size_mb)
                    self.bytes_written += bytes_written
                    self.files_created += 1
                    test_files.append(file_path)
                    file_counter += 1
                except Exception as e:
                    print(f"❌ Erreur d'écriture: {e}")
            else:  # 50% lecture
                if test_files:
                    file_path = random.choice(test_files)
                    try:
                        bytes_read = self.read_file(file_path)
                        self.bytes_read += bytes_read
                    except Exception as e:
                        print(f"❌ Erreur de lecture: {e}")
            
            self.operations_count += 1
            operation_counter += 1
            
            # Afficher la progression
            if operation_counter % 20 == 0:
                total_gb = (self.bytes_written + self.bytes_read) / (1024**3)
                print(f"   🔄 Opérations: {operation_counter} ({total_gb:.2f} GB)")
    
    def run_stress_test(self, worker_id: int = 0) -> dict:
        """
        Exécute le test de stress I/O
        
        Args:
            worker_id: Identifiant du worker
            
        Returns:
            Dictionnaire avec les statistiques du test
        """
        # Configurer l'affinité CPU
        cpu_id = self.set_cpu_affinity(worker_id)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=self.duration)
        
        print(f"🚀 Démarrage du test de stress I/O (Worker {worker_id})")
        print(f"   Durée: {self.duration} secondes")
        print(f"   Répertoire: {self.directory}")
        print(f"   Taille fichier: {self.file_size_mb} MB")
        print(f"   Opération: {self.operation}")
        print(f"   Mode SMT: {self.smt_mode}")
        if cpu_id is not None:
            print(f"   CPU assigné: {cpu_id}")
        print(f"   Début: {start_time.strftime('%H:%M:%S')}")
        print("-" * 60)
        
        # Exécuter les opérations selon le type
        if self.operation == 'write':
            self.perform_write_operations(end_time)
        elif self.operation == 'read':
            self.perform_read_operations(end_time)
        else:  # mixed
            self.perform_mixed_operations(end_time)
        
        # Calculer les statistiques
        actual_end = datetime.now()
        elapsed_seconds = (actual_end - start_time).total_seconds()
        
        stats = {
            'start_time': start_time,
            'end_time': actual_end,
            'elapsed_seconds': elapsed_seconds,
            'bytes_written': self.bytes_written,
            'bytes_read': self.bytes_read,
            'files_created': self.files_created,
            'operations_count': self.operations_count,
            'write_throughput_mbps': (self.bytes_written / (1024**2)) / elapsed_seconds if elapsed_seconds > 0 else 0,
            'read_throughput_mbps': (self.bytes_read / (1024**2)) / elapsed_seconds if elapsed_seconds > 0 else 0,
            'smt_mode': self.smt_mode,
            'cpu_id': cpu_id
        }
        
        return stats
    
    def cleanup(self):
        """Nettoie les fichiers de test"""
        print("\n🧹 Nettoyage des fichiers de test...")
        try:
            for file_path in self.directory.glob("stress_*.dat"):
                file_path.unlink()
            print("✅ Nettoyage terminé")
        except Exception as e:
            print(f"⚠️  Erreur lors du nettoyage: {e}")
    
    def display_results(self, stats: dict):
        """
        Affiche les résultats du test
        
        Args:
            stats: Dictionnaire des statistiques
        """
        print("\n" + "=" * 60)
        print("✅ TEST DE STRESS I/O TERMINÉ")
        print("=" * 60)
        print(f"Mode SMT:             {stats['smt_mode']}")
        if stats.get('cpu_id') is not None:
            print(f"CPU utilisé:          {stats['cpu_id']}")
        print(f"Début:                {stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Fin:                  {stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Durée réelle:         {stats['elapsed_seconds']:.2f} secondes")
        print(f"Opérations totales:   {stats['operations_count']:,}")
        print(f"Fichiers créés:       {stats['files_created']:,}")
        print(f"\nDonnées écrites:      {stats['bytes_written'] / (1024**3):.2f} GB")
        print(f"Débit écriture:       {stats['write_throughput_mbps']:.2f} MB/s")
        print(f"\nDonnées lues:         {stats['bytes_read'] / (1024**3):.2f} GB")
        print(f"Débit lecture:        {stats['read_throughput_mbps']:.2f} MB/s")
        print(f"\nTotal I/O:            {(stats['bytes_written'] + stats['bytes_read']) / (1024**3):.2f} GB")
        print("=" * 60)


def worker_io_process(duration: int, directory: str, file_size_mb: int, 
                      operation: str, smt_mode: int, worker_id: int):
    """
    Fonction exécutée par chaque processus worker I/O
    
    Args:
        duration: Durée du test
        directory: Répertoire de test
        file_size_mb: Taille des fichiers
        operation: Type d'opération
        smt_mode: Mode SMT
        worker_id: Identifiant du worker
    """
    worker_dir = Path(directory) / f"worker_{worker_id}"
    print(f"\n🔧 Worker I/O {worker_id} démarré (PID: {multiprocessing.current_process().pid})")
    print(f"   Répertoire: {worker_dir}")
    
    stress_test = IOStressTestSMT(duration, str(worker_dir), file_size_mb, operation, smt_mode)
    stats = stress_test.run_stress_test(worker_id)
    
    print(f"\n✅ Worker I/O {worker_id} terminé")
    print(f"   Opérations: {stats['operations_count']:,}")
    print(f"   I/O total: {(stats['bytes_written'] + stats['bytes_read']) / (1024**3):.2f} GB")
    
    return stats


def run_multi_process_io_stress(duration: int, num_processes: int, directory: str,
                                 file_size_mb: int, operation: str, smt_mode: int):
    """
    Lance un test de stress I/O sur plusieurs processus avec contrôle SMT
    
    Args:
        duration: Durée du test en secondes
        num_processes: Nombre de processus
        directory: Répertoire de test
        file_size_mb: Taille des fichiers
        operation: Type d'opération
        smt_mode: Mode SMT
    """
    print("\n" + "=" * 60)
    print("🎯 TEST DE STRESS I/O MULTI-PROCESSUS AVEC CONTRÔLE SMT")
    print("=" * 60)
    print(f"Mode SMT:            {smt_mode}")
    print(f"Nombre de processus: {num_processes}")
    print(f"Durée par processus: {duration} secondes")
    print(f"Taille fichier:      {file_size_mb} MB")
    print(f"Opération:           {operation}")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # Créer un pool de processus
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = []
        for i in range(num_processes):
            result = pool.apply_async(
                worker_io_process,
                (duration, directory, file_size_mb, operation, smt_mode, i + 1)
            )
            results.append(result)
        
        all_stats = [r.get() for r in results]
    
    end_time = datetime.now()
    total_elapsed = (end_time - start_time).total_seconds()
    
    # Calculer les statistiques globales
    total_bytes_written = sum(s['bytes_written'] for s in all_stats)
    total_bytes_read = sum(s['bytes_read'] for s in all_stats)
    total_operations = sum(s['operations_count'] for s in all_stats)
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS GLOBAUX I/O")
    print("=" * 60)
    print(f"Mode SMT:             {smt_mode}")
    print(f"Durée totale:         {total_elapsed:.2f} secondes")
    print(f"Processus utilisés:   {num_processes}")
    print(f"Opérations totales:   {total_operations:,}")
    print(f"\nDonnées écrites:      {total_bytes_written / (1024**3):.2f} GB")
    print(f"Débit écriture:       {(total_bytes_written / (1024**2)) / total_elapsed:.2f} MB/s")
    print(f"\nDonnées lues:         {total_bytes_read / (1024**3):.2f} GB")
    print(f"Débit lecture:        {(total_bytes_read / (1024**2)) / total_elapsed:.2f} MB/s")
    print(f"\nTotal I/O:            {(total_bytes_written + total_bytes_read) / (1024**3):.2f} GB")
    print("=" * 60)


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='Outil de stress test I/O avec contrôle SMT pour IBM i - Démonstrations commerciales',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  # Test d'écriture simple pendant 60 secondes en SMT 1
  python ibmi_stress_io_smt.py --duration 60 --operation write --smt 1
  
  # Test de lecture avec fichiers de 200 MB en SMT 2
  python ibmi_stress_io_smt.py --duration 120 --operation read --file-size 200 --smt 2
  
  # Test mixte sur 4 processus en SMT 4
  python ibmi_stress_io_smt.py --duration 300 --operation mixed --processes 4 --smt 4
  
  # Test intensif avec nettoyage automatique en SMT 8
  python ibmi_stress_io_smt.py --duration 600 --processes 8 --cleanup --smt 8
  
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
        '--directory',
        type=str,
        default='/tmp/ibmi_io_stress',
        help='Répertoire pour les fichiers de test (défaut: /tmp/ibmi_io_stress)'
    )
    
    parser.add_argument(
        '--file-size',
        type=int,
        default=100,
        help='Taille des fichiers en MB (défaut: 100)'
    )
    
    parser.add_argument(
        '--operation',
        choices=['read', 'write', 'mixed'],
        default='mixed',
        help='Type d\'opération (défaut: mixed)'
    )
    
    parser.add_argument(
        '--processes',
        type=int,
        default=1,
        help='Nombre de processus parallèles (défaut: 1)'
    )
    
    parser.add_argument(
        '--smt',
        type=int,
        choices=[1, 2, 4, 8],
        default=8,
        help='Mode SMT: 1, 2, 4 ou 8 threads par core (défaut: 8)'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Nettoyer les fichiers après le test'
    )
    
    args = parser.parse_args()
    
    # Valider les paramètres
    if args.duration <= 0:
        print("❌ Erreur: La durée doit être supérieure à 0")
        sys.exit(1)
    
    if args.file_size <= 0:
        print("❌ Erreur: La taille du fichier doit être supérieure à 0")
        sys.exit(1)
    
    if args.processes <= 0:
        print("❌ Erreur: Le nombre de processus doit être supérieur à 0")
        sys.exit(1)
    
    # Afficher les informations système
    print("\n" + "=" * 60)
    print("🖥️  INFORMATIONS SYSTÈME")
    print("=" * 60)
    print(f"CPUs disponibles:     {multiprocessing.cpu_count()}")
    print(f"Mode SMT configuré:   {args.smt}")
    print("=" * 60)
    
    # Lancer le test
    try:
        if args.processes == 1:
            # Test sur un seul processus
            stress_test = IOStressTestSMT(
                args.duration,
                args.directory,
                args.file_size,
                args.operation,
                args.smt
            )
            stats = stress_test.run_stress_test(1)
            stress_test.display_results(stats)
            
            if args.cleanup:
                stress_test.cleanup()
        else:
            # Test multi-processus
            run_multi_process_io_stress(
                args.duration,
                args.processes,
                args.directory,
                args.file_size,
                args.operation,
                args.smt
            )
            
            if args.cleanup:
                print("\n🧹 Nettoyage des fichiers de test...")
                import shutil
                try:
                    shutil.rmtree(args.directory)
                    print("✅ Nettoyage terminé")
                except Exception as e:
                    print(f"⚠️  Erreur lors du nettoyage: {e}")
        
        print("\n✅ Test I/O avec contrôle SMT terminé avec succès!")
        
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