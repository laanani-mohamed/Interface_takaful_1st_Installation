import polars as pl
import os
import glob
import re
from io import StringIO
from datetime import datetime


# =============================================================================
# 1. CONFIGURATION / CONSTANTES
# =============================================================================

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
BASE_FOLDER  = os.path.dirname(SCRIPT_DIR)
SOURCE_FOLDER      = os.path.join(BASE_FOLDER, "Brut")
DESTINATION_FOLDER = os.path.join(BASE_FOLDER, "Ready")
ERROR_FILE         = os.path.join(SOURCE_FOLDER, "error.txt")
MAPPING_FILE       = os.path.join(SCRIPT_DIR, "MatriceArrondiTakaful.csv")

SEUIL_POSITIF = 0.01
SEUIL_NEGATIF = -0.01

RULES = [
    # DECES
    ("DECES MT prime_TTC", "EQ", "G01", "CF01", "{prefix}{code3}-PRIME_TTC"),
    ("DECES MT prime_HT", "EQ", "G01", "CF01", "{prefix}{code3}-PRIME_HT"),
    ("DECES MT_taxe TSA", "EQ", "G01", "CF01", "{prefix}{code3}-TAXE_TSA"),
    ("DECES MT_taxe Parafiscale", "EQ", "G01", "CF01", "{prefix}{code3}-TAXE_PARAFISC"),
    ("DECES MT_chrg_gest", "EQ", "G01", "CF01", "{prefix}{code3}-CHRG_GST"),
    ("DECES MT_chrg_gest", "EQ", "G01", "CF01", "{prefix}{code3}-CHRG_GST_CP"),
    ("DECES MT_COMM TTC", "EQ", "G01", "CF01", "{prefix}{code3}-COMM_TTC"),
    ("DECES MT_COMM TTC", "EQ", "G01", "CF01", "{prefix}{code3}-COMM_TTC_CP"),

    # DTC
    ("DTC MT prime_TTC", "EQ", "G07", "CF01", "{prefix}{code3}-PRIME_TTC"),
    ("DTC MT prime_HT", "EQ", "G07", "CF01", "{prefix}{code3}-PRIME_HT"),
    ("DTC MT_taxe TSA", "EQ", "G07", "CF01", "{prefix}{code3}-TAXE_TSA"),
    ("DTC MT_taxe Parafiscale", "EQ", "G07", "CF01", "{prefix}{code3}-TAXE_PARAFISC"),
    ("DTC MT_chrg_gest", "EQ", "G07", "CF01", "{prefix}{code3}-CHRG_GST"),
    ("DTC MT_chrg_gest", "EQ", "G07", "CF01", "{prefix}{code3}-CHRG_GST_CP"),
    ("DTC MT_COMM TTC", "EQ", "G07", "CF01", "{prefix}{code3}-COMM_TTC"),
    ("DTC MT_COMM TTC", "EQ", "G07", "CF01", "{prefix}{code3}-COMM_TTC_CP"),

    # IC
    ("IC MT prime_TTC", "EQ", "G02", "CG01", "{prefix}{code3}-PRIME_TTC"),
    ("IC MT prime_HT", "EQ", "G02", "CG01", "{prefix}{code3}-PRIME_HT"),
    ("IC MT_taxe TSA", "EQ", "G02", "CG01", "{prefix}{code3}-TAXE_TSA"),
    ("IC MT_taxe Parafiscale", "EQ", "G02", "CG01", "{prefix}{code3}-TAXE_PARAFISC"),
    ("IC MT_chrg_gest", "EQ", "G02", "CG01", "{prefix}{code3}-CHRG_GST"),
    ("IC MT_chrg_gest", "EQ", "G02", "CG01", "{prefix}{code3}-CHRG_GST_CP"),
    ("IC MT_COMM TTC", "EQ", "G02", "CG01", "{prefix}{code3}-COMM_TTC"),
    ("IC MT_COMM TTC", "EQ", "G02", "CG01", "{prefix}{code3}-COMM_TTC_CP"),

    # DG
    ("DG MT prime_TTC", "EQ", "G03", "CG01", "{prefix}{code3}-PRIME_TTC"),
    ("DG MT prime_HT", "EQ", "G03", "CG01", "{prefix}{code3}-PRIME_HT"),
    ("DG MT_taxe TSA", "EQ", "G03", "CG01", "{prefix}{code3}-TAXE_TSA"),
    ("DG MT_taxe Parafiscale", "EQ", "G03", "CG01", "{prefix}{code3}-TAXE_PARAFISC"),
    ("DG MT_chrg_gest", "EQ", "G03", "CG01", "{prefix}{code3}-CHRG_GST"),
    ("DG MT_chrg_gest", "EQ", "G03", "CG01", "{prefix}{code3}-CHRG_GST_CP"),
    ("DG MT_COMM TTC", "EQ", "G03", "CG01", "{prefix}{code3}-COMM_TTC"),
    ("DG MT_COMM TTC", "EQ", "G03", "CG01", "{prefix}{code3}-COMM_TTC_CP"),

    # BG
    ("BG MT prime_TTC", "EQ", "G04", "CG01", "{prefix}{code3}-PRIME_TTC"),
    ("BG MT prime_HT", "EQ", "G04", "CG01", "{prefix}{code3}-PRIME_HT"),
    ("BG MT_taxe TSA", "EQ", "G04", "CG01", "{prefix}{code3}-TAXE_TSA"),
    ("BG MT_taxe Parafiscale", "EQ", "G04", "CG01", "{prefix}{code3}-TAXE_PARAFISC"),
    ("BG MT_chrg_gest", "EQ", "G04", "CG01", "{prefix}{code3}-CHRG_GST"),
    ("BG MT_chrg_gest", "EQ", "G04", "CG01", "{prefix}{code3}-CHRG_GST_CP"),
    ("BG MT_COMM TTC", "EQ", "G04", "CG01", "{prefix}{code3}-COMM_TTC"),
    ("BG MT_COMM TTC", "EQ", "G04", "CG01", "{prefix}{code3}-COMM_TTC_CP"),

    # EVCAT
    ("EVCAT MT prime_TTC", "EQ", "G05", "CG02", "{prefix}{code3}-PRIME_TTC"),
    ("EVCAT MT prime_HT", "EQ", "G05", "CG02", "{prefix}{code3}-PRIME_HT"),
    ("EVCAT MT_taxe TSA", "EQ", "G05", "CG02", "{prefix}{code3}-TAXE_TSA"),
    ("EVCAT MT_taxe Parafiscale", "EQ", "G05", "CG02", "{prefix}{code3}-TAXE_PARAFISC"),
    ("EVCAT MT_chrg_gest", "EQ", "G05", "CG02", "{prefix}{code3}-CHRG_GST"),
    ("EVCAT MT_chrg_gest", "EQ", "G05", "CG02", "{prefix}{code3}-CHRG_GST_CP"),
    ("EVCAT MT_COMM TTC", "EQ", "G05", "CG02", "{prefix}{code3}-COMM_TTC"),
    ("EVCAT MT_COMM TTC", "EQ", "G05", "CG02", "{prefix}{code3}-COMM_TTC_CP"),

    # LIB COMM
    ("DECES MT_COMM TTC", "ENC", "G01", "CF01", "{code03}-LIB_COMM_TTC"),
    ("DECES MT_COMM", "ENC", "G01", "CF01", "{code03}-LIB_COMM_HT"),
    ("DECES MT_taxe_comm", "ENC", "G01", "CF01", "{code03}-LIB_COMM_TAXE"),

    ("DTC MT_COMM TTC", "ENC", "G07", "CF01", "{code03}-LIB_COMM_TTC"),
    ("DTC MT_COMM", "ENC", "G07", "CF01", "{code03}-LIB_COMM_HT"),
    ("DTC MT_taxe_comm", "ENC", "G07", "CF01", "{code03}-LIB_COMM_TAXE"),

    ("IC MT_COMM TTC", "ENC", "G02", "CG01", "{code03}-LIB_COMM_TTC"),
    ("IC MT_COMM", "ENC", "G02", "CG01", "{code03}-LIB_COMM_HT"),
    ("IC MT_taxe_comm", "ENC", "G02", "CG01", "{code03}-LIB_COMM_TAXE"),

    ("DG MT_COMM TTC", "ENC", "G03", "CG01", "{code03}-LIB_COMM_TTC"),
    ("DG MT_COMM", "ENC", "G03", "CG01", "{code03}-LIB_COMM_HT"),
    ("DG MT_taxe_comm", "ENC", "G03", "CG01", "{code03}-LIB_COMM_TAXE"),

    ("BG MT_COMM TTC", "ENC", "G04", "CG01", "{code03}-LIB_COMM_TTC"),
    ("BG MT_COMM", "ENC", "G04", "CG01", "{code03}-LIB_COMM_HT"),
    ("BG MT_taxe_comm", "ENC", "G04", "CG01", "{code03}-LIB_COMM_TAXE"),

    ("EVCAT MT_COMM TTC", "ENC", "G05", "CG02", "{code03}-LIB_COMM_TTC"),
    ("EVCAT MT_COMM", "ENC", "G05", "CG02", "{code03}-LIB_COMM_HT"),
    ("EVCAT MT_taxe_comm", "ENC", "G05", "CG02", "{code03}-LIB_COMM_TAXE"),
]

PAYCLIENT_RULES = [
    ("DECES MT prime_TTC", "ENC", "G01", "CF01", "{code}-PRIME_TTC_CP"),
    ("DTC MT prime_TTC", "ENC", "G07", "CF01", "{code}-PRIME_TTC_CP"),
    ("IC MT prime_TTC", "ENC", "G02", "CG01", "{code}-PRIME_TTC_CP"),
    ("DG MT prime_TTC", "ENC", "G03", "CG01", "{code}-PRIME_TTC_CP"),
    ("BG MT prime_TTC", "ENC", "G04", "CG01", "{code}-PRIME_TTC_CP"),
    ("EVCAT MT prime_TTC", "ENC", "G05", "CG02", "{code}-PRIME_TTC_CP"),
]

COLUMNS_TO_EXPORT = [
    "CodeIFC", "NoPolice", "NoAdhesion", "NomAssure", "NomContractant", "DateEffet", 
    "DateEmission", "DateEcheance", "DateEnvoi", "DateReglement", "DateRetour", 
    "DateComptaSUNEmission", "DateComptaSUNAnnulation", "IDBand", "QuittanceNombreRepres", 
    "DateTrxPeriod", "TrxDate", "TrxReference", "TrxDescription", "Agent", "Produit", 
    "Support", "ChampLettrage", "Garantie", "CompteTakaful", "CritereCompte", "Montant",
    "Solde", "Group1", "Group2"
]


# =============================================================================
# 2. FONCTIONS UTILITAIRES
# =============================================================================

def log_error(msg: str) -> None:
    """Log un message d'erreur dans la console et dans le fichier error.txt."""
    print(msg)
    with open(ERROR_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now()} : {msg}\n")


def parse_dmy(col_name: str):
    """Retourne une expression Polars pour parser une colonne au format dd/MM/yyyy."""
    return pl.col(col_name).str.strptime(pl.Date, "%d/%m/%Y", strict=False)


def build_critere_expr(pattern: str):
    """Construit une expression Polars concat_str à partir d'un pattern avec placeholders.

    Placeholders supportés : {prefix}, {code3}, {code03}, {code}
    """
    parts = []
    rest = pattern
    while rest:
        m = re.search(r'\{([^}]+)\}', rest)
        if not m:
            parts.append(pl.lit(rest))
            break

        if m.start() > 0:
            parts.append(pl.lit(rest[:m.start()]))

        key = m.group(1)
        if key == "prefix":
            parts.append(pl.col("detail_prefix"))
        elif key == "code3":
            parts.append(pl.col("code3"))
        elif key == "code03":
            parts.append(pl.col("code03"))
        elif key == "code":
            parts.append(pl.col("code"))

        rest = rest[m.end():]
    return pl.concat_str(parts)


def fmt_num(v) -> str:
    """Formate un nombre flottant en string avec 2 décimales max, sans zéros trailing.

    Exemples : 12.00 -> '12' | 12.30 -> '12.3' | 12.34 -> '12.34'
    """
    if v is None:
        return ""
    s = format(v, ".2f")
    return s.rstrip("0").rstrip(".") if "." in s else s


# =============================================================================
# 3. CHARGEMENT DES DONNÉES DE RÉFÉRENCE
# =============================================================================

def load_mapping_matrix(mapping_path: str) -> pl.DataFrame:
    """Charge la matrice d'arrondi et renomme la colonne ID en CritereCompte.

    Args:
        mapping_path: Chemin vers le fichier CSV MatriceArrondiTakaful.csv

    Returns:
        DataFrame Polars avec les colonnes CritereCompte et Data

    Raises:
        Exception si le fichier est introuvable ou illisible
    """
    return pl.read_csv(mapping_path, separator=";", infer_schema_length=0).rename(
        {"ID": "CritereCompte"}
    )


# =============================================================================
# 4. PRÉPARATION DU FICHIER SOURCE (NETTOYAGE)
# =============================================================================

def clean_raw_content(file_path: str) -> str:
    """Lit un fichier brut et applique les nettoyages syntaxiques (réplique PowerShell).

    Étapes :
        1. Lecture en latin-1 avec ignore des erreurs
        2. Collapse des espaces multiples en un seul espace (par ligne)
        3. Remplacement des accents, virgules, nulls, etc.

    Args:
        file_path: Chemin du fichier source

    Returns:
        Contenu nettoyé sous forme de string
    """
    with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
        content = f.read()

    # Remplace les espaces multiples par un seul espace, ligne par ligne
    content = '\n'.join([re.sub(r'\s+', ' ', line) for line in content.splitlines()])

    # Nettoyages divers (réplique exacte du script PS1)
    content = content.replace(' ;', ';').replace('è', 'e').replace('é', 'e').replace('ê', 'e')
    content = content.replace(',', ';').replace('null;', ';').replace('NULL;', ';')

    return content


def read_source_dataframe(content: str) -> pl.DataFrame:
    """Parse un contenu CSV nettoyé en DataFrame Polars (tout en String).

    Args:
        content: Contenu CSV nettoyé

    Returns:
        DataFrame Polars avec toutes les colonnes en Utf8
    """
    return pl.read_csv(StringIO(content), separator=";", infer_schema_length=0)


# =============================================================================
# 5. IDENTIFICATION ET FILTRAGE PAR TYPE DE FICHIER
# =============================================================================

def detect_file_type(df: pl.DataFrame) -> tuple[bool, bool, str]:
    """Détecte si le fichier est de type ENC, AQ ou inconnu.

    Args:
        df: DataFrame source

    Returns:
        Tuple (is_enc, is_aq, first_code)
    """
    if df.height == 0:
        return False, False, ""

    first_code = df[0, "Code d'actes de Gestion"]
    is_enc = first_code.startswith("ENC") if first_code else False
    is_aq = first_code.startswith("AQ") if first_code else False
    return is_enc, is_aq, first_code


def filter_rows_by_type(df: pl.DataFrame, is_enc: bool, is_aq: bool) -> pl.DataFrame:
    """Filtre les lignes selon le type de fichier détecté.

    - ENC : garde uniquement les lignes avec Date Reglement non vide
    - AQ  : garde uniquement les lignes où le 3ème caractère du code est 'P'

    Args:
        df: DataFrame source
        is_enc: True si fichier ENC
        is_aq: True si fichier AQ

    Returns:
        DataFrame filtré
    """
    if is_enc:
        return df.filter(pl.col("Date Reglement").str.len_chars() > 0)
    elif is_aq:
        return df.filter(pl.col("Code d'actes de Gestion").str.slice(2, 1) == "P")
    return df


# =============================================================================
# 6. NORMALISATION DES COLONNES
# =============================================================================

def normalize_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Normalise les noms de colonnes (case-insensitive) et garantit l'existence
    des colonnes de base en les créant vides si absentes.

    Args:
        df: DataFrame source

    Returns:
        DataFrame avec colonnes normalisées
    """
    base_cols = [
        "Code d'actes de Gestion", "Police", "Quittance", "Nom Assure", "Nom Contractant",
        "Date Effet", "Date emission", "Date Echeance", "Date envoi", "Date Reglement", "Date annulation",
        "ID Band", "quittance_nbr_repres", "Tiers", "code_produit"
    ]

    # Rename case-insensitively
    rename_map = {}
    for col in df.columns:
        for bc in base_cols:
            if col.lower().strip() == bc.lower().strip():
                rename_map[col] = bc

    if rename_map:
        df = df.rename(rename_map)

    # Crée les colonnes manquantes avec valeur vide
    for c in base_cols:
        if c not in df.columns:
            df = df.with_columns(pl.lit("").alias(c))

    return df


# =============================================================================
# 7. CONSTRUCTION DES COLONNES DÉRIVÉES
# =============================================================================

def build_derived_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Crée toutes les colonnes dérivées nécessaires au traitement métier.

    Colonnes créées :
        - code, police_int_str, quittance, nom_assure, nom_contractant
        - code3 (sans les 3 premiers caractères), code03 (3 premiers caractères)
        - detail_prefix (EQ ou AQ)
        - trx_date_dt (date de transaction parsée)
        - trx_date, trx_period (formats ddMMyyyy et 0MMyyyy)
        - eq_date_* (dates formatées pour les écritures EQ)
        - eq_trx_ref, eq_trx_desc, enc_trx_ref, enc_trx_desc

    Args:
        df: DataFrame avec colonnes normalisées

    Returns:
        DataFrame enrichi
    """
    df = df.with_columns([
        pl.col("Code d'actes de Gestion").alias("code"),
        pl.col("Police").cast(pl.Int64, strict=False).cast(pl.Utf8).fill_null("").alias("police_int_str"),
        pl.col("Quittance").alias("quittance"),
        pl.col("Nom Assure").str.head(30).fill_null("").alias("nom_assure"),
        pl.col("Nom Contractant").str.head(30).fill_null("").alias("nom_contractant"),
        pl.col("Code d'actes de Gestion").str.slice(3).alias("code3"),
        pl.col("Code d'actes de Gestion").str.head(3).alias("code03"),
    ])

    df = df.with_columns([
        pl.when(pl.col("code").str.starts_with("ENC")).then(pl.lit("EQ"))
          .when(pl.col("code").str.starts_with("AQ")).then(pl.lit("AQ"))
          .otherwise(pl.lit("")).alias("detail_prefix"),
    ])

    df = df.with_columns([
        pl.when(pl.col("code").str.starts_with("ENC")).then(parse_dmy("Date Reglement"))
          .when(pl.col("code").str.starts_with("AQ")).then(parse_dmy("Date annulation"))
          .otherwise(pl.lit(None)).alias("trx_date_dt")
    ])

    df = df.with_columns([
        pl.col("trx_date_dt").dt.strftime("%d%m%Y").fill_null("").alias("trx_date"),
        (pl.lit("0") + pl.col("trx_date_dt").dt.strftime("%m%Y")).fill_null("").alias("trx_period"),

        parse_dmy("Date Effet").dt.strftime("%d%m%Y").fill_null("").alias("eq_date_effet"),
        parse_dmy("Date emission").dt.strftime("%d%m%Y").fill_null("").alias("eq_date_emission"),
        parse_dmy("Date Echeance").dt.strftime("%d%m%Y").fill_null("").alias("eq_date_echeance"),
        parse_dmy("Date envoi").dt.strftime("%d%m%Y").fill_null("").alias("eq_date_envoi"),
        parse_dmy("Date Reglement").dt.strftime("%d%m%Y").fill_null("").alias("eq_date_reglement"),

        pl.when(pl.col("code").str.starts_with("ENC")).then(pl.lit("EQ") + pl.col("code3") + "-" + pl.col("quittance"))
          .when(pl.col("code").str.starts_with("AQ")).then(pl.lit("AQ") + pl.col("code3") + "-" + pl.col("quittance"))
          .otherwise(pl.lit("")).alias("eq_trx_ref"),

        pl.when(pl.col("code").str.starts_with("ENC")).then(pl.lit("EQ") + pl.col("code3") + "- Quittance:" + pl.col("quittance") + "- Police:" + pl.col("Police"))
          .when(pl.col("code").str.starts_with("AQ")).then(pl.lit("AQ") + pl.col("code3") + "- Quittance:" + pl.col("quittance") + "- Police:" + pl.col("Police"))
          .otherwise(pl.lit("")).alias("eq_trx_desc"),

        pl.when(pl.col("code").str.starts_with("ENC")).then(pl.lit("ENC") + pl.col("code3") + "-" + pl.col("quittance"))
          .when(pl.col("code").str.starts_with("AQ")).then(pl.lit("AENC") + pl.col("code3") + "-" + pl.col("quittance"))
          .otherwise(pl.lit("")).alias("enc_trx_ref"),

        pl.when(pl.col("code").str.starts_with("ENC")).then(pl.lit("ENC") + pl.col("code3") + "- Quittance:" + pl.col("quittance") + "- Police:" + pl.col("Police"))
          .when(pl.col("code").str.starts_with("AQ")).then(pl.lit("AENC") + pl.col("code3") + "- Quittance:" + pl.col("quittance") + "- Police:" + pl.col("Police"))
          .otherwise(pl.lit("")).alias("enc_trx_desc"),
    ])

    return df


# =============================================================================
# 8. GÉNÉRATION DES ÉCRITURES COMPTABLES (UNPIVOT / MELT MANUEL)
# =============================================================================

def generate_accounting_entries(df: pl.DataFrame, is_enc_file: bool) -> list[pl.DataFrame]:
    """Génère les lignes d'écritures comptables à partir des règles métier.

    Pour chaque règle dans RULES (+ PAYCLIENT_RULES si ENC), filtre les lignes
    où le montage source est non nul et non zéro, puis sélectionne les colonnes
    au format attendu par SUN.

    Args:
        df: DataFrame enrichi avec colonnes dérivées
        is_enc_file: True si fichier ENC (pour ajouter les règles PAYCLIENT)

    Returns:
        Liste de DataFrames (un par règle appliquée)
    """
    output_dfs = []
    all_rules = RULES.copy()
    if is_enc_file:
        all_rules.extend(PAYCLIENT_RULES)

    for src_col, hdr_type, gar, cpt, crit_pat in all_rules:
        if src_col not in df.columns:
            continue

        rule_df = df.filter(
            (pl.col(src_col).is_not_null()) & (pl.col(src_col) != "0.0")
        )
        if rule_df.height == 0:
            continue

        sel = rule_df.select([
            pl.col("code").alias("CodeIFC"),
            pl.col("police_int_str").alias("NoPolice"),
            pl.col("quittance").alias("NoAdhesion"),
            pl.col("nom_assure").alias("NomAssure"),
            pl.col("nom_contractant").alias("NomContractant"),

            (pl.col("eq_date_effet") if hdr_type == "EQ" else pl.lit("")).alias("DateEffet"),
            (pl.col("eq_date_emission") if hdr_type == "EQ" else pl.lit("")).alias("DateEmission"),
            (pl.col("eq_date_echeance") if hdr_type == "EQ" else pl.lit("")).alias("DateEcheance"),
            (pl.col("eq_date_envoi") if hdr_type == "EQ" else pl.lit("")).alias("DateEnvoi"),
            (pl.col("eq_date_reglement") if hdr_type == "EQ" else pl.lit("")).alias("DateReglement"),
            pl.lit("").alias("DateRetour"),
            pl.lit("").alias("DateComptaSUNEmission"),
            pl.lit("").alias("DateComptaSUNAnnulation"),

            pl.col("ID Band").cast(pl.Utf8).str.strip_chars().alias("IDBand"),
            pl.col("quittance_nbr_repres").alias("QuittanceNombreRepres"),
            pl.col("trx_period").alias("DateTrxPeriod"),
            pl.col("trx_date").alias("TrxDate"),

            (pl.col("eq_trx_ref") if hdr_type == "EQ" else pl.col("enc_trx_ref")).alias("TrxReference"),
            (pl.col("eq_trx_desc") if hdr_type == "EQ" else pl.col("enc_trx_desc")).alias("TrxDescription"),

            pl.col("Tiers").alias("Agent"),
            pl.col("code_produit").alias("Produit"),
            pl.lit("A00").alias("Support"),
            pl.col("quittance").alias("ChampLettrage"),

            pl.lit(gar).alias("Garantie"),
            pl.lit(cpt).alias("CompteTakaful"),
            build_critere_expr(crit_pat).alias("CritereCompte"),
            pl.col(src_col).alias("Montant")
        ])
        output_dfs.append(sel)

    return output_dfs


# =============================================================================
# 9. GÉNÉRATION DU RÉSUMÉ BANCAIRE
# =============================================================================

def generate_bank_summary(df: pl.DataFrame, is_enc_file: bool) -> pl.DataFrame | None:
    """Génère les lignes de résumé bancaire (IFCSummaryPayBanque).

    Agrège les MT prime_TTC par (code, Date Reglement) et formate une ligne
    comptable de type banque avec Agent=BF001 et CompteTakaful=CG02.

    Args:
        df: DataFrame enrichi
        is_enc_file: True si fichier ENC (sinon retourne None)

    Returns:
        DataFrame des lignes banque, ou None si non applicable
    """
    if not is_enc_file or "MT prime_TTC" not in df.columns:
        return None

    bank_df = df.filter(
        (pl.col("MT prime_TTC").is_not_null()) & 
        (pl.col("MT prime_TTC") != "0.0") & 
        (pl.col("MT prime_TTC") != "0")
    )

    if bank_df.height == 0:
        return None

    bank_summary = bank_df.with_columns(
        pl.col("MT prime_TTC").str.replace(",", ".").cast(pl.Float64, strict=False)
    ).group_by(["code", "Date Reglement"]).agg(
        pl.col("MT prime_TTC").sum().round(2).alias("Somme")
    )

    bank_sel = bank_summary.with_columns([
        parse_dmy("Date Reglement").dt.strftime("%d%m%Y").fill_null("").alias("TrxDate"),
        (pl.lit("0") + parse_dmy("Date Reglement").dt.strftime("%m%Y")).fill_null("").alias("DateTrxPeriod")
    ]).select([
        pl.col("code").alias("CodeIFC"),
        pl.lit("").alias("NoPolice"),
        pl.lit("").alias("NoAdhesion"),
        pl.lit("").alias("NomAssure"),
        pl.lit("").alias("NomContractant"),
        pl.lit("").alias("DateEffet"),
        pl.lit("").alias("DateEmission"),
        pl.lit("").alias("DateEcheance"),
        pl.lit("").alias("DateEnvoi"),
        pl.col("TrxDate").alias("DateReglement"),
        pl.lit("").alias("DateRetour"),
        pl.lit("").alias("DateComptaSUNEmission"),
        pl.lit("").alias("DateComptaSUNAnnulation"),
        pl.lit("").alias("IDBand"),
        pl.lit("").alias("QuittanceNombreRepres"),
        pl.col("DateTrxPeriod"),
        pl.col("TrxDate"),
        (pl.col("code") + " " + pl.col("TrxDate")).alias("TrxReference"),
        (pl.col("code") + " " + pl.col("TrxDate")).alias("TrxDescription"),
        pl.lit("BF001").alias("Agent"),
        pl.lit("").alias("Produit"),
        pl.lit("").alias("Support"),
        pl.lit("").alias("ChampLettrage"),
        pl.lit("").alias("Garantie"),
        pl.lit("CG02").alias("CompteTakaful"),
        (pl.col("code") + "TTLBANQUE").alias("CritereCompte"),
        pl.col("Somme").cast(pl.Utf8).alias("Montant")
    ])

    return bank_sel


# =============================================================================
# 10. CALCUL DES ÉCARTS D'ARRONDI
# =============================================================================

def compute_rounding_diffs(rnd_df: pl.DataFrame, mapping_df: pl.DataFrame) -> pl.DataFrame:
    """Calcule les écarts d'arrondi par groupe (Group1, Group2).

    Étapes :
        1. Jointure avec la matrice d'arrondi sur CritereCompte
        2. Calcul du Solde = Montant * Data (arrondi à 2 décimales)
        3. Construction des clés Group1 / Group2 (logique hardcodée PS1)
        4. Agrégation de la somme des Soldes par groupe -> colonne Difference

    Args:
        rnd_df: DataFrame concaténé de toutes les écritures
        mapping_df: Matrice d'arrondi chargée

    Returns:
        DataFrame enrichi avec Solde, Group1, Group2, Difference
    """
    # Jointure matrice
    rnd_df = rnd_df.join(
        mapping_df.select(["CritereCompte", "Data"]),
        on="CritereCompte",
        how="left"
    )

    # Calcul du Solde
    rnd_df = rnd_df.with_columns([
        pl.col("Montant").cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64, strict=False).fill_null(0.0).round(2).alias("montant_num"),
        pl.col("Data").cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64, strict=False).fill_null(0.0).round(2).alias("data_num")
    ]).with_columns(
        (pl.col("montant_num") * pl.col("data_num")).round(2).alias("Solde")
    )

    # Construction Group1 / Group2 (réplique exacte PS1)
    rnd_df = rnd_df.with_columns([
        pl.when(pl.col("CritereCompte").str.head(2) == "EQ").then(pl.col("Garantie"))
          .when(pl.col("CritereCompte").is_in(["ENCADE-PRIME_TTC_CP", "ENCADETTLBANQUE"])).then(pl.lit("ENCADE"))
          .when(pl.col("CritereCompte").is_in(["ENCMRB-PRIME_TTC_CP", "ENCMRBTTLBANQUE"])).then(pl.lit("ENCMRB"))
          .when(pl.col("CritereCompte").str.head(12) == "ENC-LIB_COMM").then(pl.lit("ENCLIBCOMM"))
          .otherwise(pl.lit("")).alias("Group1"),

        pl.when(pl.col("CritereCompte").str.head(2) == "EQ").then(pl.col("NoAdhesion"))
          .when(pl.col("CritereCompte").is_in(["ENCADE-PRIME_TTC_CP", "ENCADETTLBANQUE"])).then(pl.col("TrxDate"))
          .when(pl.col("CritereCompte").is_in(["ENCMRB-PRIME_TTC_CP", "ENCMRBTTLBANQUE"])).then(pl.col("TrxDate"))
          .when(pl.col("CritereCompte").str.head(12) == "ENC-LIB_COMM").then(pl.col("TrxDate"))
          .otherwise(pl.lit("")).alias("Group2"),
    ])

    # Calcul de la différence par groupe
    diff_df = rnd_df.group_by(["Group1", "Group2"]).agg([
        pl.col("Solde").sum().round(2).alias("Difference")
    ])

    rnd_df = rnd_df.join(diff_df, on=["Group1", "Group2"], how="left")
    return rnd_df


# =============================================================================
# 11. GÉNÉRATION DES LIGNES DE REDRESSEMENT (ÉCARTS)
# =============================================================================

def generate_balancing_rows(rnd_df: pl.DataFrame) -> pl.DataFrame:
    """Génère les lignes de redressement pour les groupes déséquilibrés.

    Pour chaque groupe où |Difference| > 0, crée une ligne d'écart avec :
        - Montant = abs(Difference)
        - Solde = -Difference
        - CritereCompte adapté selon les seuils (ECARTPOSITIF, ECARTNEGATIF, etc.)

    Args:
        rnd_df: DataFrame avec colonnes Difference calculées

    Returns:
        DataFrame final incluant les lignes d'écart
    """
    diff_blocks = rnd_df.filter(pl.col("Difference").abs() > 0.0)

    if diff_blocks.height == 0:
        return rnd_df

    # Prend la première ligne de chaque groupe déséquilibré comme template
    template_rows = diff_blocks.group_by(["Group1", "Group2"], maintain_order=True).first()

    balancing_rows = template_rows.with_columns([
        pl.col("Difference").abs().cast(pl.Utf8).alias("Montant"),
        (-pl.col("Difference")).alias("Solde"),

        pl.when((pl.col("Difference") <= SEUIL_POSITIF) & (pl.col("Difference") > 0.0))
          .then(pl.col("CritereCompte").str.head(2) + "-ECARTPOSITIF")
          .when((pl.col("Difference") >= SEUIL_NEGATIF) & (pl.col("Difference") < 0.0))
          .then(pl.col("CritereCompte").str.head(2) + "-ECARTNEGATIF")
          .when(pl.col("Difference") < SEUIL_NEGATIF)
          .then(pl.col("CritereCompte").str.head(2) + "-GRANDECARTN")
          .when(pl.col("Difference") > SEUIL_POSITIF)
          .then(pl.col("CritereCompte").str.head(2) + "-GRANDECARTP")
          .otherwise(pl.col("CritereCompte")).alias("CritereCompte")
    ]).select(rnd_df.columns)

    final_df = pl.concat([rnd_df, balancing_rows], how="vertical")
    return final_df


# =============================================================================
# 12. FORMATAGE FINAL DES NOMBRES
# =============================================================================

def format_output_numbers(final_df: pl.DataFrame) -> pl.DataFrame:
    """Formate les colonnes Montant et Solde pour l'export SUN.

    - Montant : format anglais (point décimal), sans trailing zeros
    - Solde   : format français (virgule décimale), sans trailing zeros

    Args:
        final_df: DataFrame avec colonnes Montant et Solde brutes

    Returns:
        DataFrame formaté avec sélection des colonnes d'export
    """
    final_df = final_df.with_columns([
        pl.col("Montant").cast(pl.Utf8)
            .str.replace(",", ".")
            .alias("Montant"),
        pl.col("Solde")
            .cast(pl.Float64, strict=False)
            .map_elements(lambda v: fmt_num(v).replace(".", ","), return_dtype=pl.Utf8)
            .alias("Solde")
    ]).select(COLUMNS_TO_EXPORT)

    return final_df


# =============================================================================
# 13. EXPORT DES FICHIERS FINaux (.SUN et .csv)
# =============================================================================

def export_final_files(final_df: pl.DataFrame, base_name: str, destination_folder: str) -> None:
    """Exporte le DataFrame final en fichiers .SUN et .csv.

    Caractéristiques :
        - Séparateur point-virgule
        - Pas de guillemets
        - Fins de ligne CRLF (\r\n)
        - Encodage ASCII
        - Pas de ligne vide finale

    Args:
        final_df: DataFrame formaté prêt à l'export
        base_name: Nom de base du fichier (sans extension)
        destination_folder: Dossier de destination
    """
    sun_path = os.path.join(destination_folder, f"{base_name}.SUN")
    csv_path = os.path.join(destination_folder, f"{base_name}.csv")

    csv_content = final_df.write_csv(separator=";", quote_style="never", line_terminator="\r\n")
    csv_content = csv_content.rstrip("\r\n")

    for out_path in (sun_path, csv_path):
        with open(out_path, "w", encoding="ascii", errors="ignore", newline="") as f:
            f.write(csv_content)

    print(f"Fichiers générés : {sun_path} et {csv_path}")


# =============================================================================
# 14. ORCHESTRATION PRINCIPALE
# =============================================================================

def process_single_file(file_path: str, mapping_df: pl.DataFrame) -> None:
    """Traite un fichier source de bout en bout.

    Pipeline :
        1. Nettoyage du contenu brut
        2. Lecture en DataFrame
        3. Détection du type (ENC/AQ)
        4. Filtrage des lignes
        5. Normalisation des colonnes
        6. Construction des colonnes dérivées
        7. Génération des écritures comptables
        8. Génération du résumé bancaire
        9. Concaténation et calcul des écarts
        10. Génération des lignes d'écart
        11. Formatage et export

    Args:
        file_path: Chemin du fichier source à traiter
        mapping_df: Matrice d'arrondi déjà chargée
    """
    print(f"Préparation du fichier : {file_path} : Phase 1.")

    # Étape 1 & 2 : Nettoyage et lecture
    content = clean_raw_content(file_path)
    df = read_source_dataframe(content)

    if df.height == 0:
        return

    # Étape 3 : Détection type
    is_enc, is_aq, first_code = detect_file_type(df)
    if not is_enc and not is_aq:
        print(f"Fichier ignoré car code non reconnu: {first_code}")
        return

    # Étape 4 : Filtrage
    df = filter_rows_by_type(df, is_enc, is_aq)
    if df.height == 0:
        return

    print(f"Préparation du fichier : {file_path} : Phase 2.")

    # Étape 5 : Normalisation colonnes
    df = normalize_columns(df)

    # Étape 6 : Colonnes dérivées
    df = build_derived_columns(df)

    # Étape 7 : Écritures comptables
    output_dfs = generate_accounting_entries(df, is_enc)

    # Étape 8 : Résumé bancaire
    bank_df = generate_bank_summary(df, is_enc)
    if bank_df is not None:
        output_dfs.append(bank_df)

    if not output_dfs:
        return

    # Concaténation (équivalent du .RND)
    rnd_df = pl.concat(output_dfs, how="vertical")

    # Étape 9 : Écarts d'arrondi
    rnd_df = compute_rounding_diffs(rnd_df, mapping_df)

    # Étape 10 : Lignes de redressement
    final_df = generate_balancing_rows(rnd_df)

    # Étape 11 : Formatage et export
    final_df = format_output_numbers(final_df)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    export_final_files(final_df, base_name, DESTINATION_FOLDER)


def process_files() -> None:
    """Point d'entrée principal : traite tous les fichiers du dossier Brut."""
    try:
        mapping_df = load_mapping_matrix(MAPPING_FILE)
    except Exception as e:
        log_error(f"Erreur chargement matrice d'arrondi : {str(e)}")
        return

    search_pattern = os.path.join(SOURCE_FOLDER, "*.*")
    for file_path in glob.glob(search_pattern):
        if os.path.isdir(file_path) or file_path == MAPPING_FILE:
            continue

        try:
            process_single_file(file_path, mapping_df)
        except Exception as e:
            log_error(f"Erreur lors du traitement de {file_path} : {str(e)}")


if __name__ == '__main__':
    process_files()
