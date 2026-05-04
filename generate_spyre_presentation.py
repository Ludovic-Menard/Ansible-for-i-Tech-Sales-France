#!/usr/bin/env python3
"""
Générateur de présentation PowerPoint pour les cartes Spyre sur IBM Power11
Inclut les cas d'usage et la partie commerciale
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor

def create_title_slide(prs, title, subtitle):
    """Crée une diapositive de titre"""
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = title
    slide.placeholders[1].text = subtitle
    return slide

def create_content_slide(prs, title, content_items):
    """Crée une diapositive avec titre et contenu à puces"""
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = title
    
    body_shape = slide.placeholders[1]
    tf = body_shape.text_frame
    tf.clear()
    
    for item in content_items:
        p = tf.add_paragraph()
        p.text = item
        p.level = 0
        p.font.size = Pt(18)
    
    return slide

def create_two_column_slide(prs, title, left_content, right_content):
    """Crée une diapositive avec deux colonnes"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = title
    
    # Colonne gauche
    left_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(4.5), Inches(5))
    tf_left = left_box.text_frame
    tf_left.word_wrap = True
    for item in left_content:
        p = tf_left.add_paragraph()
        p.text = item
        p.font.size = Pt(14)
    
    # Colonne droite
    right_box = slide.shapes.add_textbox(Inches(5.2), Inches(1.5), Inches(4.5), Inches(5))
    tf_right = right_box.text_frame
    tf_right.word_wrap = True
    for item in right_content:
        p = tf_right.add_paragraph()
        p.text = item
        p.font.size = Pt(14)
    
    return slide

def create_table_slide(prs, title, headers, rows):
    """Crée une diapositive avec un tableau"""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = title
    
    # Créer le tableau
    rows_count = len(rows) + 1
    cols_count = len(headers)
    left = Inches(1)
    top = Inches(2)
    width = Inches(8)
    height = Inches(0.5)
    
    table = slide.shapes.add_table(rows_count, cols_count, left, top, width, height).table
    
    # En-têtes
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0, 112, 192)
        cell.text_frame.paragraphs[0].font.bold = True
        cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.text_frame.paragraphs[0].font.size = Pt(14)
    
    # Données
    for i, row in enumerate(rows):
        for j, cell_text in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.text = str(cell_text)
            cell.text_frame.paragraphs[0].font.size = Pt(12)
    
    return slide

def main():
    """Génère la présentation complète"""
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    
    # Slide 1: Page de titre
    create_title_slide(
        prs,
        "Cartes Spyre sur IBM Power11",
        "Accélération IA/ML pour IBM i\nCas d'usage et Offre Commerciale"
    )
    
    # Slide 2: Vue d'ensemble
    create_content_slide(
        prs,
        "Vue d'ensemble des cartes Spyre",
        [
            "Accélérateurs PCIe Gen5 pour IA et Machine Learning",
            "Intégration native avec IBM Power11 et IBM i",
            "Performance jusqu'à 25x supérieure pour les tâches ML",
            "Support TensorFlow, PyTorch, ONNX Runtime",
            "Pas de migration nécessaire - Intégration transparente"
        ]
    )
    
    # Slide 3: Architecture technique
    create_content_slide(
        prs,
        "Architecture d'intégration",
        [
            "Connexion PCIe directe au système Power11",
            "API REST pour intégration depuis RPG/COBOL/SQL",
            "Stored Procedures SQL pour appels simplifiés",
            "Support Python via PASE pour développements avancés",
            "Isolation et sécurité au niveau partition"
        ]
    )
    
    # Slide 4: Cas d'usage 1 - Banque
    create_two_column_slide(
        prs,
        "Cas d'usage 1: Détection de Fraude (Banque)",
        [
            "CONTEXTE:",
            "• Analyse temps réel des transactions",
            "• Détection de patterns frauduleux",
            "• Intégration avec DB2 for i",
            "",
            "SOLUTION SPYRE:",
            "• 10 000+ transactions/seconde",
            "• Analyse en moins de 50ms",
            "• Modèle ML de détection d'anomalies"
        ],
        [
            "BÉNÉFICES:",
            "• Réduction de 95% du temps de détection",
            "• Diminution de 70% des faux positifs",
            "• Aucun impact sur applications métier",
            "",
            "ROI:",
            "• Économie: 500K€/an",
            "• Retour sur investissement: 18 mois",
            "• Amélioration satisfaction client"
        ]
    )
    
    # Slide 5: Cas d'usage 2 - Manufacturing
    create_two_column_slide(
        prs,
        "Cas d'usage 2: Optimisation Chaîne Logistique",
        [
            "CONTEXTE:",
            "• Gestion stocks et production sur IBM i",
            "• Prévisions de demande complexes",
            "• Optimisation inventaire",
            "",
            "SOLUTION SPYRE:",
            "• Prédiction de demande ML",
            "• Calcul temps réel niveaux optimaux",
            "• Planification production dynamique"
        ],
        [
            "RÉSULTATS:",
            "• Réduction 30% ruptures de stock",
            "• Diminution 25% coûts inventaire",
            "• Amélioration 40% précision prévisions",
            "",
            "IMPACT BUSINESS:",
            "• Économie: 1.2M€/an",
            "• Amélioration service client",
            "• Optimisation trésorerie"
        ]
    )
    
    # Slide 6: Cas d'usage 3 - Retail
    create_two_column_slide(
        prs,
        "Cas d'usage 3: Analyse Sentiment Client (Retail)",
        [
            "CONTEXTE:",
            "• Milliers d'avis clients quotidiens",
            "• Analyse manuelle impossible",
            "• Besoin insights temps réel",
            "",
            "SOLUTION SPYRE:",
            "• NLP accéléré sur Spyre",
            "• Classification sentiment automatique",
            "• Extraction insights récurrents"
        ],
        [
            "PERFORMANCE:",
            "• 50 000 avis traités/heure",
            "• Précision 92% classification",
            "• Temps réponse: 100ms/avis",
            "",
            "VALEUR AJOUTÉE:",
            "• Réactivité améliorée",
            "• Identification problèmes rapide",
            "• Tableaux de bord temps réel"
        ]
    )
    
    # Slide 7: Cas d'usage 4 - Industrie
    create_two_column_slide(
        prs,
        "Cas d'usage 4: Maintenance Prédictive",
        [
            "CONTEXTE:",
            "• Équipements industriels connectés",
            "• Données IoT sur IBM i",
            "• Coûts arrêts production élevés",
            "",
            "SOLUTION SPYRE:",
            "• Analyse séries temporelles",
            "• Prédiction pannes 7-14 jours avance",
            "• 1000+ capteurs temps réel"
        ],
        [
            "ROI EXCEPTIONNEL:",
            "• Réduction 45% arrêts non planifiés",
            "• Économie: 2M€/an maintenance",
            "• +15% disponibilité équipements",
            "",
            "DONNÉES TRAITÉES:",
            "• Température, vibrations, électricité",
            "• 5 ans historique maintenance",
            "• Corrélation multi-sources"
        ]
    )
    
    # Slide 8: Cas d'usage 5 - Finance
    create_two_column_slide(
        prs,
        "Cas d'usage 5: Scoring Crédit Avancé",
        [
            "CONTEXTE:",
            "• Évaluation demandes crédit",
            "• Modèles complexes nécessaires",
            "• Décision rapide requise",
            "",
            "SOLUTION SPYRE:",
            "• Réseaux neurones profonds",
            "• 200+ critères évaluation",
            "• Réponse en moins de 2 secondes"
        ],
        [
            "AVANTAGES:",
            "• 5000 demandes traitées/jour",
            "• +35% précision scoring",
            "• -60% temps traitement",
            "",
            "INTÉGRATION RPG:",
            "• Appel natif depuis RPG",
            "• Approbation automatique",
            "• Traçabilité complète"
        ]
    )
    
    # Slide 9: Autres cas d'usage
    create_content_slide(
        prs,
        "Autres cas d'usage Spyre",
        [
            "Télécoms: Détection anomalies réseau et prévention fraude",
            "E-commerce: Recommandations produits et pricing dynamique",
            "Assurance: OCR et analyse automatique de documents",
            "Santé: Analyse d'images médicales et diagnostics assistés",
            "Transport: Optimisation routes et maintenance prédictive"
        ]
    )
    
    # Slide 10: Comparaison performance
    create_table_slide(
        prs,
        "Comparaison Performance: CPU vs Spyre",
        ["Tâche", "CPU seul", "Avec Spyre", "Gain"],
        [
            ["Inférence ML (1000 req)", "45s", "2s", "22.5x"],
            ["Analyse NLP (10k docs)", "180s", "8s", "22.5x"],
            ["Vision par ordinateur", "300s", "12s", "25x"],
            ["Détection anomalies", "90s", "4s", "22.5x"]
        ]
    )
    
    # Slide 11: Prérequis techniques
    create_two_column_slide(
        prs,
        "Prérequis Techniques",
        [
            "MATÉRIEL:",
            "• IBM Power11 (S1014, S1022s, S1024, E1050)",
            "• Carte Spyre PCIe Gen5",
            "• Minimum 64GB RAM",
            "• IBM i 7.5 TR2 ou supérieur",
            "",
            "LOGICIEL:",
            "• IBM i Access Client Solutions",
            "• Python 3.9+ (via PASE)",
            "• Node.js (optionnel)"
        ],
        [
            "RÉSEAU:",
            "• Connectivité PCIe interne",
            "• API REST pour intégration",
            "• Message broker (optionnel)",
            "",
            "SÉCURITÉ:",
            "• Isolation par partition",
            "• Chiffrement données transit",
            "• Audit complet des accès",
            "• Conformité RGPD, PCI-DSS, SOX"
        ]
    )
    
    # Slide 12: Roadmap implémentation
    create_content_slide(
        prs,
        "Roadmap d'Implémentation",
        [
            "Phase 1 - POC (2-4 semaines): Installation, config, test modèle",
            "Phase 2 - Développement (6-8 semaines): API, modèles métier, tests",
            "Phase 3 - Pilote (4-6 semaines): Déploiement use case, monitoring",
            "Phase 4 - Production (2-4 semaines): Déploiement complet, support",
            "Durée totale: 14-22 semaines selon complexité"
        ]
    )
    
    # Slide 13: OFFRE COMMERCIALE - Titre
    create_title_slide(
        prs,
        "Offre Commerciale Bundle Spyre",
        "Configuration Power11 avec accélération IA"
    )
    
    # Slide 14: Configuration P11 recommandée
    create_content_slide(
        prs,
        "Configuration IBM Power11 Recommandée",
        [
            "Modèle: IBM Power S1024 (Scale-out 4U)",
            "Processeurs: 2x Power11 (24 cores activés)",
            "Mémoire: 256GB DDR5",
            "Stockage: 4x 1.92TB SSD NVMe + contrôleur RAID",
            "Carte Spyre: 1x Spyre PCIe Gen5 Accelerator",
            "OS: IBM i 7.5 TR3 + licences utilisateurs"
        ]
    )
    
    # Slide 15: Bundle Spyre - Détails
    create_two_column_slide(
        prs,
        "Bundle Spyre pour Power11 - Détails",
        [
            "MATÉRIEL INCLUS:",
            "• Serveur Power11 S1024",
            "• 1x Carte Spyre PCIe Gen5",
            "• Configuration réseau redondante",
            "• Rails rack + câbles",
            "",
            "LOGICIELS INCLUS:",
            "• IBM i 7.5 TR3",
            "• Spyre SDK et Runtime",
            "• Outils développement ML",
            "• Ansible pour IBM i"
        ],
        [
            "SERVICES INCLUS:",
            "• Installation et configuration",
            "• Formation 3 jours équipe technique",
            "• POC sur 1 cas d'usage",
            "• Support 12 mois (9x5)",
            "",
            "OPTIONS:",
            "• Support 24x7 (+15%)",
            "• Cartes Spyre additionnelles",
            "• Services développement ML",
            "• Formation avancée"
        ]
    )
    
    # Slide 16: Tarification
    create_table_slide(
        prs,
        "Tarification Bundle Spyre P11",
        ["Composant", "Prix Unitaire", "Quantité", "Total"],
        [
            ["Power11 S1024 configuré", "185 000 €", "1", "185 000 €"],
            ["Carte Spyre PCIe Gen5", "45 000 €", "1", "45 000 €"],
            ["IBM i 7.5 + licences (50 users)", "35 000 €", "1", "35 000 €"],
            ["Services installation/formation", "15 000 €", "1", "15 000 €"],
            ["Support 12 mois (9x5)", "12 000 €", "1", "12 000 €"],
            ["", "", "TOTAL HT", "292 000 €"]
        ]
    )
    
    # Slide 17: Options et extensions
    create_table_slide(
        prs,
        "Options et Extensions",
        ["Option", "Description", "Prix"],
        [
            ["Carte Spyre additionnelle", "Scaling performance IA", "45 000 €"],
            ["Support 24x7", "Support premium 24h/24", "+15% annuel"],
            ["Formation ML avancée", "5 jours développement ML", "8 500 €"],
            ["Services développement", "Développement modèles custom", "1 200 €/jour"],
            ["Stockage additionnel", "4x 3.84TB SSD NVMe", "18 000 €"],
            ["Mémoire additionnelle", "+256GB DDR5", "22 000 €"]
        ]
    )
    
    # Slide 18: Modèles de financement
    create_two_column_slide(
        prs,
        "Modèles de Financement Disponibles",
        [
            "ACHAT DIRECT:",
            "• Investissement: 292 000 € HT",
            "• Propriété immédiate",
            "• Amortissement 3-5 ans",
            "",
            "LOCATION FINANCIÈRE (36 mois):",
            "• Mensualité: 8 900 € HT",
            "• Option d'achat en fin de contrat",
            "• Préservation trésorerie"
        ],
        [
            "LOCATION OPÉRATIONNELLE (36 mois):",
            "• Mensualité: 9 500 € HT",
            "• Upgrade technologique inclus",
            "• Charges déductibles 100%",
            "",
            "PAY-PER-USE (Cloud):",
            "• Facturation à l'usage",
            "• Flexibilité maximale",
            "• Idéal pour POC/pilotes"
        ]
    )
    
    # Slide 19: ROI et bénéfices
    create_two_column_slide(
        prs,
        "ROI et Bénéfices Business",
        [
            "GAINS QUANTIFIABLES:",
            "• Performance ML: 20-25x plus rapide",
            "• Réduction coûts infra IA: 30-40%",
            "• Économies opérationnelles: 500K-2M€/an",
            "• Pas de migration nécessaire",
            "",
            "ROI MOYEN:",
            "• Retour sur investissement: 18-24 mois",
            "• Break-even typique: 15-20 mois"
        ],
        [
            "BÉNÉFICES STRATÉGIQUES:",
            "• Innovation sans disruption",
            "• Time-to-market réduit",
            "• Avantage compétitif IA",
            "• Valorisation données existantes",
            "",
            "RISQUES MINIMISÉS:",
            "• Pas de réécriture applications",
            "• Compétences IBM i préservées",
            "• Évolution progressive"
        ]
    )
    
    # Slide 20: Comparaison alternatives
    create_table_slide(
        prs,
        "Comparaison avec Alternatives",
        ["Critère", "Spyre sur P11", "Cloud IA", "Serveurs x86"],
        [
            ["Coût 3 ans", "350K €", "600K €", "450K €"],
            ["Performance ML", "Excellente", "Bonne", "Moyenne"],
            ["Intégration IBM i", "Native", "API externe", "Complexe"],
            ["Latence", "<5ms", "50-200ms", "10-50ms"],
            ["Sécurité données", "Locale", "Cloud", "Locale"],
            ["Compétences requises", "IBM i existantes", "Cloud + ML", "x86 + ML"]
        ]
    )
    
    # Slide 21: Témoignages clients
    create_content_slide(
        prs,
        "Témoignages Clients (Anonymisés)",
        [
            "Banque européenne: 'Détection fraude 95% plus rapide, ROI en 16 mois'",
            "Manufacturier: 'Réduction 30% ruptures stock, 1.2M€ économisés/an'",
            "Assureur: 'Traitement documents 80% plus rapide, 10 ETP économisés'",
            "Retailer: 'Recommandations temps réel, +25% panier moyen'",
            "Industriel: 'Maintenance prédictive, -45% arrêts, 2M€ économisés/an'"
        ]
    )
    
    # Slide 22: Prochaines étapes
    create_content_slide(
        prs,
        "Prochaines Étapes",
        [
            "1. Atelier découverte: Identification cas d'usage prioritaires (1 jour)",
            "2. Démonstration technique: POC sur vos données (2 jours)",
            "3. Étude ROI personnalisée: Calcul bénéfices spécifiques (1 semaine)",
            "4. Proposition commerciale détaillée: Devis et planning (1 semaine)",
            "5. Démarrage projet: Commande et kick-off (selon planning)"
        ]
    )
    
    # Slide 23: Support et accompagnement
    create_two_column_slide(
        prs,
        "Support et Accompagnement IBM",
        [
            "SUPPORT TECHNIQUE:",
            "• Hotline dédiée Spyre",
            "• Accès portail support IBM",
            "• Mises à jour firmware/software",
            "• Documentation complète",
            "",
            "FORMATION:",
            "• IBM Skills Gateway",
            "• Cours Spyre SDK",
            "• Workshops techniques",
            "• Certification disponible"
        ],
        [
            "ÉCOSYSTÈME PARTENAIRES:",
            "• Intégrateurs certifiés",
            "• ISV avec solutions ML",
            "• Communauté développeurs",
            "• Forums et ressources",
            "",
            "ÉVOLUTION PRODUIT:",
            "• Roadmap Spyre publique",
            "• Nouvelles fonctionnalités",
            "• Compatibilité garantie",
            "• Migration facilitée"
        ]
    )
    
    # Slide 24: Contact et questions
    create_content_slide(
        prs,
        "Contact et Questions",
        [
            "Équipe IBM Power Systems France",
            "Email: power-sales-france@ibm.com",
            "Téléphone: +33 1 XX XX XX XX",
            "",
            "Ressources en ligne:",
            "• ibm.com/power/spyre",
            "• Documentation technique: ibm.com/docs/power11",
            "• Communauté: community.ibm.com/power"
        ]
    )
    
    # Slide 25: Conclusion
    create_title_slide(
        prs,
        "Merci de votre attention",
        "Questions ?"
    )
    
    # Sauvegarder la présentation
    filename = "Presentation_Spyre_IBM_Power11_Commercial.pptx"
    prs.save(filename)
    print(f"✅ Présentation créée avec succès: {filename}")
    print(f"📊 Nombre de slides: {len(prs.slides)}")
    print(f"📁 Fichier: {filename}")

if __name__ == "__main__":
    main()

# Made with Bob
