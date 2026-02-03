#!/usr/bin/env python
"""Script pour adapter le projet au contexte camerounais avec franc CFA"""

import os
import re

# Répertoire des templates
template_dir = "banking/templates/banking"

# Remplacements à effectuer
replacements = [
    ("€", "F CFA"),
]

def replace_in_file(filepath):
    """Remplacer les motifs dans un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Écrire seulement si le contenu a changé
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Modifié: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"✗ Erreur dans {filepath}: {e}")
        return False

def main():
    print("🇨🇲 Adaptation au contexte camerounais - Franc CFA\n")
    
    count = 0
    for filename in os.listdir(template_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(template_dir, filename)
            if replace_in_file(filepath):
                count += 1
    
    print(f"\n✓ {count} fichier(s) modifié(s)")

if __name__ == "__main__":
    main()
