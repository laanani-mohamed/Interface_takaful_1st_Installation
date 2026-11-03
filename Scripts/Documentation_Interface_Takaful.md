# Interface Takaful – Documentation du traitement

Script : Scripts/Interface_Takaful.py (lancé par Launcher.bat)

## 1. Objectif

Le script transforme les fichiers CSV bruts d'encaissements (ENC) et d'annulations de quittances (AQ) exportés du système Takaful en un fichier d'écritures comptables au format attendu par SUN Systems. Il produit, pour chaque fichier source, un fichier .SUN et un fichier .csv de contenu identique, après avoir corrigé les écarts d'arrondi par des lignes de redressement.

## 2. Arborescence et fichiers utilisés

| Élément | Rôle |
|---|---|
| Brut/ | Dossier d'entrée : fichiers *.csv à traiter |
| Ready/ | Dossier de sortie : fichiers .SUN et .csv générés |
| Brut/error.txt | Journal des erreurs (horodaté) |
| Scripts/MatriceArrondiTakaful.csv | Matrice d'arrondi (colonnes ID;Data) : coefficient (1 / -1) par critère de compte |
| Scripts/Launcher.bat | Prépare Python portable, installe les paquets locaux (setup/), puis lance le script |

## 3. Lancement

1. Placer les CSV à traiter dans le dossier Brut.

2. Exécuter Scripts/Launcher.bat : il vérifie python_portable, installe pip si besoin, installe les wheels de Scripts/setup (polars, myutils) puis exécute Interface_Takaful.py.

3. Récupérer les fichiers générés dans le dossier Ready.

## 4. Déroulement du traitement

Le traitement est exécuté fichier par fichier (boucle sur Brut/*.csv). Une erreur sur un fichier est journalisée dans error.txt et n'empêche pas le traitement des suivants.

### 4.1 Chargement de la matrice d'arrondi

Le fichier MatriceArrondiTakaful.csv (séparateur « ; ») est lu en texte et sa colonne ID est renommée CritereCompte. En cas d'échec, l'erreur est journalisée et le script s'arrête.

### 4.2 Phase 1 – Nettoyage du texte

- Lecture du fichier en latin-1.

- Réduction de toute suite d'espaces à un seul espace, par ligne.

- Suppression des espaces avant « ; ».

- Remplacement des caractères accentués è, é, ê par e.

- Remplacement de la virgule par « ; » et suppression des valeurs « null; » / « NULL; ».

- Lecture avec Polars, toutes les colonnes forcées en texte (pour conserver les zéros de tête).

### 4.3 Identification du type de fichier et filtrage

Le type est déterminé par la colonne « Code d'actes de Gestion » de la première ligne :

| Code | Type | Filtre |
|---|---|---|
| Commence par ENC | Encaissement | On ne garde que les lignes dont « Date Reglement » est renseignée |
| Commence par AQ | Annulation de quittance | On ne garde que les lignes dont le 3e caractère du code est « P » |
| Autre | Non reconnu | Fichier ignoré (message affiché) |

Un fichier vide ou sans ligne après filtrage est ignoré.

### 4.4 Phase 2 – Normalisation des colonnes

Les colonnes attendues (Code d'actes de Gestion, Police, Quittance, Nom Assure, Nom Contractant, Date Effet, Date emission, Date Echeance, Date envoi, Date Reglement, Date annulation, ID Band, quittance_nbr_repres, Tiers, code_produit) sont renommées sans tenir compte de la casse ; celles qui manquent sont créées vides.

### 4.5 Colonnes dérivées

| Colonne | Contenu |
|---|---|
| code / code03 / code3 | Code complet / 3 premiers caractères / reste du code |
| police_int_str | Police convertie en entier (supprime les zéros de tête et décimales) |
| nom_assure, nom_contractant | Tronqués à 30 caractères |
| detail_prefix | « EQ » pour ENC, « AQ » pour AQ |
| trx_date | Date de règlement (ENC) ou d'annulation (AQ), format JJMMAAAA |
| trx_period | « 0 » + MMAAAA de la date de transaction |
| eq_date_* | Dates Effet, émission, échéance, envoi, règlement au format JJMMAAAA |
| TrxReference / TrxDescription | EQ/AQ + code3 + « - » + quittance ; description avec « Quittance: » et « Police: ». Pour les lignes ENC (hors EQ) : préfixe ENC ou AENC |

### 4.6 Éclatement des montants en écritures (unpivot)

Chaque ligne source contient plusieurs montants (un par garantie et par nature). Le script parcourt la liste de règles RULES (et PAYCLIENT_RULES pour les fichiers ENC) et génère, pour chaque règle dont la colonne source est présente et non nulle / différente de « 0.0 », une écriture. Une règle = (colonne source, type d'en-tête EQ/ENC, garantie, compte Takaful, modèle de critère de compte).

| Garantie métier | Code garantie | Compte Takaful |
|---|---|---|
| DECES | G01 | CF01 |
| DTC | G07 | CF01 |
| IC | G02 | CG01 |
| DG | G03 | CG01 |
| BG | G04 | CG01 |
| EVCAT | G05 | CG02 |

Natures de montants traitées par garantie et critères de compte générés :

| Colonne source (préfixée par la garantie) | Type | Critère de compte |
|---|---|---|
| MT prime_TTC | EQ | {prefix}{code3}-PRIME_TTC |
| MT prime_HT | EQ | {prefix}{code3}-PRIME_HT |
| MT_taxe TSA | EQ | {prefix}{code3}-TAXE_TSA |
| MT_taxe Parafiscale | EQ | {prefix}{code3}-TAXE_PARAFISC |
| MT_chrg_gest | EQ | {prefix}{code3}-CHRG_GST et -CHRG_GST_CP (2 écritures) |
| MT_COMM TTC | EQ | {prefix}{code3}-COMM_TTC et -COMM_TTC_CP (2 écritures) |
| MT_COMM TTC | ENC | {code03}-LIB_COMM_TTC (libération commission) |
| MT_COMM | ENC | {code03}-LIB_COMM_HT |
| MT_taxe_comm | ENC | {code03}-LIB_COMM_TAXE |
| MT prime_TTC (fichiers ENC) | ENC | {code}-PRIME_TTC_CP (paiement client) |

Pour le type EQ, les dates (effet, émission, échéance, envoi, règlement) sont renseignées ; pour le type ENC elles sont vides. Les champs fixes : Support = « A00 », Agent = colonne Tiers, Produit = code_produit, ChampLettrage = numéro de quittance.

### 4.7 Ligne de synthèse bancaire

Pour les fichiers ENC, une ligne par couple (code, Date Reglement) est ajoutée : somme de « MT prime_TTC » arrondie à 2 décimales, avec Agent « BF001 », compte « CG02 », critère de compte = code + « TTLBANQUE » et référence = code + date.

### 4.8 Traitement des écarts d'arrondi

1. Toutes les écritures sont concaténées (équivalent de l'ancien fichier .RND).

2. Jointure avec la matrice d'arrondi sur CritereCompte pour obtenir le coefficient Data (1 ou -1).

3. Solde = Montant × Data, arrondi à 2 décimales.

4. Construction des clés de regroupement : Group1 / Group2 = (Garantie, NoAdhesion) pour les critères EQ…, (ENCADE, date) pour ENCADE, (ENCMRB, date) pour ENCMRB, (ENCLIBCOMM, date) pour ENC-LIB_COMM…

5. Pour chaque groupe, Difference = somme des Solde.

6. Si Difference ≠ 0, une ligne d'équilibrage est ajoutée (Montant = |Difference|, Solde = -Difference) avec un critère de compte parmi : xx-ECARTPOSITIF / xx-ECARTNEGATIF (écart d'au plus 0,01) ou xx-GRANDECARTP / xx-GRANDECARTN (écart supérieur à 0,01), où xx = 2 premiers caractères du critère d'origine.

### 4.9 Export

- 30 colonnes, dans l'ordre : CodeIFC, NoPolice, NoAdhesion, NomAssure, NomContractant, DateEffet, DateEmission, DateEcheance, DateEnvoi, DateReglement, DateRetour, DateComptaSUNEmission, DateComptaSUNAnnulation, IDBand, QuittanceNombreRepres, DateTrxPeriod, TrxDate, TrxReference, TrxDescription, Agent, Produit, Support, ChampLettrage, Garantie, CompteTakaful, CritereCompte, Montant, Solde, Group1, Group2.

- Montant : séparateur décimal point. Solde : séparateur décimal virgule, 2 décimales sans zéros inutiles.

- Séparateur « ; », sans guillemets, fins de ligne CRLF, encodage ASCII (caractères non ASCII supprimés), sans ligne vide finale (rejetée par le logiciel d'upload).

- Deux fichiers identiques : Ready/<nom>.SUN et Ready/<nom>.csv.

## 5. Gestion des erreurs

- Toute exception est affichée à l'écran et ajoutée dans Brut/error.txt avec date, heure et trace technique.

- Fichiers ignorés sans erreur : vides, code non reconnu, aucune ligne après filtrage, aucune écriture générée.

## 6. Points d'attention

- Le dossier Brut ne doit contenir que des CSV à traiter ; chaque *.csv est traité.

- Un fichier de sortie existant du même nom dans Ready est écrasé.

- Toute nouvelle garantie ou nature de montant s'ajoute dans la liste RULES ; tout nouveau critère de compte doit figurer dans MatriceArrondiTakaful.csv, sinon son coefficient vaut 0 et son Solde est nul.

- Le script Interface_Takaful_modular.py est une version modulaire distincte ; Launcher.bat lance Interface_Takaful.py.
