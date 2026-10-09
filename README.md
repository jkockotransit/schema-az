# schema-az — icônes officielles Microsoft pour schémas d'architecture

Bibliothèque unique des icônes officielles Microsoft, lue par Claude (génération de schémas PowerPoint et draw.io) et directement par draw.io. Elle est reconstruite par GitHub Actions à partir des packs publiés par Microsoft.

Ce dépôt est public : il ne contient que des icônes Microsoft et du code. Aucune donnée interne ni client.

| Famille | Source officielle |
|---|---|
| Azure | https://learn.microsoft.com/azure/architecture/icons/ |
| Power Platform | https://learn.microsoft.com/power-platform/guidance/icons |
| Microsoft Entra | https://learn.microsoft.com/entra/architecture/architecture-icons |
| Microsoft Fabric | https://learn.microsoft.com/fabric/get-started/icons |
| Dynamics 365 | https://learn.microsoft.com/dynamics365/get-started/icons |
| Microsoft 365 (jeu archivé, figé) | https://learn.microsoft.com/microsoft-365/solutions/architecture-icons-templates |

## Contenu

- `icons/<famille>/<catégorie>/<icône>.svg` : icônes extraites des packs officiels (PNG si le pack ne fournit pas de SVG).
- `drawio/<famille>.xml` : bibliothèques draw.io, icônes intégrées et utilisables hors ligne. Azure est aussi découpé par catégorie (`drawio/azure-<catégorie>.xml`).
- `index.json` : catalogue des icônes (famille, catégorie, nom, chemin, adresse brute).
- `manifest.json` : version, date, lien de téléchargement et empreinte de chaque pack.
- `sources.json` : où trouver chaque pack. `scripts/build.py` : script de construction (Python 3.9 ou plus, bibliothèque standard).

Les dossiers `icons/`, `drawio/` et les fichiers `index.json`, `manifest.json` sont écrits uniquement par l'automatisation.

## Mettre à jour

Onglet **Actions** > **Construire la bibliothèque d'icônes** > **Run workflow**. Le script retélécharge les packs Microsoft et ne modifie que les familles dont le pack a changé. Cocher « forcer » pour tout reconstruire. Après l'exécution, faire **Fetch origin** puis **Pull origin** dans GitHub Desktop pour mettre à jour la copie locale.

## Ouvrir dans draw.io

- Web, les 6 bibliothèques préchargées : https://app.diagrams.net/?splash=0&clibs=Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjkockotransit%2Fschema-az%2Fmain%2Fdrawio%2Fazure.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjkockotransit%2Fschema-az%2Fmain%2Fdrawio%2Fpower-platform.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjkockotransit%2Fschema-az%2Fmain%2Fdrawio%2Fentra.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjkockotransit%2Fschema-az%2Fmain%2Fdrawio%2Ffabric.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjkockotransit%2Fschema-az%2Fmain%2Fdrawio%2Fdynamics-365.xml;Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fjkockotransit%2Fschema-az%2Fmain%2Fdrawio%2Fmicrosoft-365.xml
- Web, une seule bibliothèque : menu **Fichier > Ouvrir une bibliothèque depuis > URL**, puis coller l'adresse brute d'un fichier, par exemple `https://raw.githubusercontent.com/jkockotransit/schema-az/main/drawio/azure.xml`.
- Desktop : **Fichier > Ouvrir une bibliothèque**, puis choisir un fichier de `C:\Dev\Pro\schema-az\drawio\`. draw.io desktop fonctionne hors ligne et ne propose pas l'ouverture par URL : la copie locale, mise à jour par **Pull origin**, est la source.

## Conditions d'utilisation

Les icônes appartiennent à Microsoft Corporation. Microsoft en autorise l'usage dans des schémas d'architecture, des supports de formation et de la documentation : ne pas les recadrer, retourner, pivoter ni déformer, et ne pas les utiliser pour représenter un autre produit. Les icônes Entra ne doivent pas servir dans des communications marketing. Se référer aux pages officielles ci-dessus.
