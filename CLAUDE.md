# schema-az

Contexte : Pro
Architecture : conforme à REGLES-ARCHITECTURE.md v1.7 (dépôt de ressources publiques, section 5 : dépôt public, bibliothèque écrite par l'automatisation, exception E0021)

## Emplacements

| Rôle | Chemin |
|---|---|
| Code (dépôt Git) | `C:\Dev\Pro\schema-az\` |
| Dépôt GitHub | `https://github.com/jkockotransit/schema-az` (**public**, exception E0021) |
| Documents | `<OneDrive>\Pro\schema-az\Documents\` |
| Base de connaissance (cahier des charges, CONTEXTE-PROJET.md) | `<OneDrive>\Pro\schema-az\Base-connaissance\` |
| Visuels hors dépôt (schémas de test) | `<OneDrive>\Pro\schema-az\Visuels\` |
| Configuration locale | aucune (pas de `.env`) |
| Modèles d'IA, datasets | aucun |
| Éléments communs utilisés | aucun |

Cahier des charges de référence : `<OneDrive>\Pro\schema-az\Base-connaissance\SchemaAz_Cahier-des-charges_V1.3.md`.

## Pour Claude

- Lire ce fichier et `README.md` avant toute modification ; dans le projet Cowork « schema-az », lire aussi `CONTEXTE-PROJET.md`.
- Dépôt **public** : n'y placer que des icônes Microsoft et du code. Jamais de donnée Orange, client ou personnelle, jamais de schéma client, jamais de document Office.
- Exception E0021 : seul le workflow GitHub Actions écrit `icons/`, `drawio/`, `index.json` et `manifest.json`. Ne jamais les modifier à la main.
- `scripts/build.py` n'écrit que dans le dépôt, avec des chemins relatifs à sa racine : `chemins.py` n'est pas utilisé.
- Python 3.9 ou plus, bibliothèque standard uniquement (`requirements.txt` vide).
- Ne jamais faire de commit ni de push : Jacky publie le code avec GitHub Desktop ; le workflow se lance seulement après son accord dans le chat.
- Guides liés à mettre à jour si l'organisation change : cahier des charges schema-az (Word et Markdown), procédure Word, CONTEXTE-PROJET.md, plugin schema-az du catalogue jko-plugins-pro.
