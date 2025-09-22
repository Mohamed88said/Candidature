#!/usr/bin/env python
import os
import shutil

def fix_static_files():
    """Corrige les problèmes de fichiers statiques"""
    
    # Chemins
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, 'static')
    
    # Créer les dossiers s'ils n'existent pas
    folders = ['css', 'js', 'images']
    for folder in folders:
        folder_path = os.path.join(static_dir, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"✓ Créé: {folder_path}")
    
    # Vérifier les fichiers CSS
    css_files = ['custom.css', 'mobile.css']
    for css_file in css_files:
        css_path = os.path.join(static_dir, 'css', css_file)
        if not os.path.exists(css_path):
            # Créer un fichier CSS par défaut
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(f"/* {css_file} - Fichier créé automatiquement */\n")
                f.write("body { background-color: #f8f9fa; }\n")
            print(f"✓ Créé: {css_path}")
    
    # Vérifier le fichier JS
    js_path = os.path.join(static_dir, 'js', 'custom.js')
    if not os.path.exists(js_path):
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write("// custom.js - Fichier créé automatiquement\n")
            f.write("console.log('Custom JS loaded');\n")
        print(f"✓ Créé: {js_path}")
    
    print("✓ Tous les fichiers statiques sont prêts !")

if __name__ == "__main__":
    fix_static_files()