import os

# Dossiers Ã  exclure
EXCLUS = {'venv', 'env', '__pycache__', '.git', '.idea', 'node_modules', 'migrations', '.vscode'}

# Nom du fichier de sortie
FICHIER_SORTIE = "arborescence.txt"

def afficher_arborescence(racine, fichier, niveau=0):
    try:
        elements = sorted(os.listdir(racine))
    except PermissionError:
        return

    for nom in elements:
        if nom in EXCLUS:
            continue
        chemin = os.path.join(racine, nom)
        indent = "â”‚   " * niveau
        if os.path.isdir(chemin):
            fichier.write(f"{indent}â”œâ”GNFâ”GNF {nom}/\n")
            afficher_arborescence(chemin, fichier, niveau + 1)
        elif os.path.isfile(chemin):
            fichier.write(f"{indent}â”œâ”GNFâ”GNF {nom}\n")

def main():
    dossier_racine = "."  # Dossier actuel
    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        f.write("Arborescence du projet :\n")
        f.write("â”œâ”GNFâ”GNF .\n")
        afficher_arborescence(dossier_racine, f, 1)

    print(f"âœ… Fichier '{FICHIER_SORTIE}' gÃ©nÃ©rÃ© avec succÃ¨s.")

if __name__ == "__main__":
    main()


