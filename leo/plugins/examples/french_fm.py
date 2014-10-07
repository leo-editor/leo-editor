# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:EKR.20040517080202.3: * @file examples/french_fm.py
#@@first

"""traduit les menus en Français"""

#@@language python
#@@tabwidth -4

# French translation completed by Frédéric Momméja, Spring 2003

import leo.core.leoGlobals as g

__version__ = "1.4" # Set version for the plugin handler.

#@+others
#@+node:ekr.20111104210837.9688: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = g.unitTesting
        # Unpleasant for unit testing.
    if ok:
        # Register the handlers...
        g.registerHandler("menu2", onMenu)
        g.plugin_signon(__name__)
    return ok
#@+node:EKR.20040517080202.4: ** onMenu
def onMenu (tag,keywords):
    c = keywords.get("c")
    table = (
        ("File","&Fichier"),
            ("New","&Nouveau"),
            ("Open...","&Ouvrir"),
            ("OpenWith","Ouvrir Ave&c..."),
            ("Close","&Fermer"),
            ("Save","Enregi&strer"),
            ("Save As","Enre&gistrer sous..."),
            ("Save To","Enregistrer une co&pie..."),
            ("Revert To Saved","&Version Enregistrée"),
            ("Recent Files...","&Fichiers récents..."),
            ("Read/Write...", "&Lire/Écrire..."),
                ("Read Outline Only", "Relire &Arborescence seule"),
                ("Read @file Nodes", "Relire Structure @&file seule"),
                ("Write missing @file Nodes", "Écrire @file &manquants sur Disque"),
                ("Write Outline Only", "Écrire Arborescence &seule"),
                ("Write @file Nodes", "Écrire &Noeuds @file seuls"),
            ("Tangle...", "&Transférer (Tangle)..."),
                ("Tangle All", "&Tout"),
                ("Tangle Marked", "Noeuds &Marqués"),
                ("Tangle", "&Sélection"),
            ("Untangle...", "&Ramener (Untangle)..."),
                ("Untangle All", "&Tout"),
                ("Untangle Marked", "Noeuds &Marqués"),
                ("Untangle", "&Sélection"),
            ("Import...", "&Importer..."),
                ("Import To @file", "Dans Structure @&file"),
                ("Import To @root", "Dans Structure @&root"),
                ("Import CWEB Files", "Fichier &CWEB"),
                ("Import noweb Files", "Fichier &Noweb"),
                ("Import Flattened Outline", "Fichier &MORE"),
            ("Export...", "&Exporter..."),
                ("Export Headlines", "&Entêtes Noeuds descendants vers .txt"),
                ("Outline To CWEB", "Arborescence vers &CWEB"),
                ("Outline To Noweb", "Arborescence vers &Noweb"),
                ("Flatten Outline", "Arborescence vers &MORE"),
                ("Remove Sentinels", "En supprimant &Sentinelles"),
                ("Weave", "&Arborescence descendante vers .txt"),
            ("Exit","&Quitter"),
        ("Edit","&Edition"),
            ("Undo Typing","Ann&uler saisie"),
            ("Redo Typing","&Répèter saisie"),
            ("Can't Undo", "Impossible d'annuler"),
            ("Can't Redo", "Impossible de répéter"),
            ("Cut", "C&ouper"),
            ("Copy", "Co&pier"),
            ("Paste", "Co&ller"),
            ("Delete", "&Supprimer"),
            ("Select All", "&Tout Sélectionner"),
            ("Edit Body...", "Éditer &Contenu..."),
                ("Extract Section", "E&xtraire Section"),
                ("Extract Names", "Extraire &Noms de Sections"),
                ("Extract", "&Extraire Sélection"),
                ("Convert All Blanks", "Convertir Espaces &Arborescence"),
                ("Convert All Tabs", "Convertir Tabulations Ar&borescence"),
                ("Convert Blanks", "Convertir &Espaces"),
                ("Convert Tabs", "Convertir &Tabulations"),
                ("Insert Body Time/Date", "Insérer la &Date/Heure"),
                ("Reformat Paragraph", "Reformater &Paragraphe"),
                ("Indent", "&Indenter"),
                ("Unindent", "Dé&sindenter"),
                ("Match Brackets", "&Vérifier Parité des Signes"), #  <({["), #EKR
            ("Edit Headline...", "Éditer &Entête..."),
                ("Edit Headline", "&Modifier l'Entête"),
                ("End Edit Headline", "Modification &Terminée"),
                ("Abort Edit Headline", "&Annuler Modification"),
                ("Insert Headline Time/Date", "Insérer la &Date/Heure"),
                ("Toggle Angle Brackets", "Ajouter/supprimer Marques de &Section"),
            ("Find...", "C&hercher..."),
                ("Find Panel", "Dialogue de Re&cherche"),
                ("Find Next", "Chercher &Suivant"),
                ("Find Previous", "Chercher &Précédent"),
                ("Replace", "&Remplacer"),
                ("Replace, Then Find", "Remplacer Chercher à &Nouveau"),
            ("Go To Line Number", "&Atteindre Ligne No..."),
            ("Execute Script", "E&xécuter un Script Python"),
            ("Set Font...", "&Définir les Polices..."),
            ("Set Colors...", "Dé&finir les Couleurs..."),
            ("Show Invisibles", "Afficher Caractères &invisibles"),
            ("Hide Invisibles", "Masquer Caractères &invisibles"),
            ("Preferences", "Préfére&nces"),
        ("Outline", "Arb&orescence"),
            ("Cut Node", "Co&uper le Noeud"),
            ("Copy Node", "C&opier le Noeud"),
            ("Paste Node", "Co&ller le Noeud"),
            ("Delete Node", "&Supprimer le Noeud"),
            ("Insert Node", "Insé&rer un Noeud"),
            ("Clone Node", "Clo&ner le Noeud"),
            ("Sort Children", "&Trier les Noeuds Enfants"),
            ("Sort Siblings", "Trier le Ni&veau"),
            ("Expand/Contract...", "&Déployer/Refermer"),
                ("Contract All", "&Tout Refermer"),
                ("Contract Node", "&Refermer Noeud"),
                ("Contract Parent", "Refermer Noeud &Parent"),
                ("Expand Prev Level", "Déployer Niveau pré&cédent"),
                ("Expand Next Level", "Déployer Niveau &suivant"),
                ("Expand To Level 1", "Déployer &1 Niveau"),
                ("Expand To Level 2", "Déployer &2 Niveaux"),
                ("Expand To Level 3", "Déployer &3 Niveaux"),
                ("Expand To Level 4", "Déployer &4 Niveaux"),
                ("Expand To Level 5", "Déployer &5 Niveaux"),
                ("Expand To Level 6", "Déployer &6 Niveaux"),
                ("Expand To Level 7", "Déployer &7 Niveaux"),
                ("Expand To Level 8", "Déployer &8 Niveaux"),
                ("Expand All", "Tout &Déployer"),
                ("Expand Node", "Déplo&yer Noeud"),
            ("Move...", "Dé&placer..."),
                ("Move Down", "Vers le &Bas"),
                ("Move Left", "Vers la &Gauche"),
                ("Move Right", "Vers la &Droite"),
                ("Move Up", "Vers le &Haut"),
                ("Promote", "&Enfants vers la Gauche"),
                ("Demote", "&Noeuds suivants vers la Droite"),
            ("Mark/Unmark...", "Mar&quage..."),
                ("Mark", "&Marquer/Effacer Marque"),
                ("Mark Subheads", "Marquer En&fants"),
                ("Mark Changed Items", "Marquer &Noeuds modifiés"),
                ("Mark Changed Roots", "Marquer @&root modifiés"),
                ("Mark Clones", "Marquer &Clones"),
                ("Unmark All", "&Effacer toutes les Marques"),
            ("Go To...", "Se Dépla&cer vers..."),
                ("Go To Next Marked", "&Marque suivante"),
                ("Go To Next Changed", "M&odification suivante"),
                ("Go To Next Clone", "&Clone suivant"),
                ("Go To First Node", "&Premier Noeud"),
                ("Go To Last Node", "&Dernier Noeud"),
                ("Go To Parent", "&Noeud Parent"),
                ("Go To Prev Sibling", "Noe&ud précédent"),
                ("Go To Next Sibling", "Noeud &suivant"),
                ("Go To Prev Visible", "Noeud &Visible précédent"),
                ("Go To Next Visible", "Noeud V&isible suivant"),
                ("Go Back", "De&rnière Position"),
                ("Go Next", "Posi&tion suivante"),
        ("Window", "Fenê&tre"),
            ("Equal Sized Panes", "Panneaux de &même taille"),
            ("Toggle Active Pane", "&Bascule Panneau actif"),
            ("Toggle Split Direction", "Bascule &Horiz/Vert"),
            ("Cascade", "Fenêtres Leo en &Cascade"),
            ("Minimize All", "&Réduit toutes les Fenêtres"),
            ("Open Compare Window", "Ouvrir Fenêtre de Com&paraison..."),
            ("Open Python Window", "Ouvrir Fenêtre Python (IDLE)..."),
        ("Help", "&Aide"),
            ("About Leo...", "Au &sujet de Leo..."),
            ("Online Home Page", "&Page d'Accueil en ligne"),
            ("Open Online Tutorial", "Ouvrir &Tutoriel en ligne"),
            ("Open LeoDocs.leo", "Ouvrir Leo&Docs.leo"),
            ("Open LeoConfig.leo", "Ouvrir Leo&Config.leo"),
            ("Apply Settings", "Appliquer les &Réglages"))
    # Call the convenience routine to do the work.
    c.frame.menu.setRealMenuNamesFromTable(table)

#@-others
#@-leo
