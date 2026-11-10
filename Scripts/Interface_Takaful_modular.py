"""
Interface Takaful -> SUN (version modulaire)

Pipeline (une fonction par etape) :
    1. clean_source_text      : nettoyage syntaxique du fichier brut
    2. load_source_df         : lecture Polars (tout en String)
    3. detect_file_type       : ENC (encaissement) ou AQ (annulation)
    4. filter_rows            : filtre principal selon le type
    5. ensure_base_columns    : normalisation / creation des colonnes requises
    6. add_derived_columns    : dates, references, descriptions
    7. build_detail_lines     : "unpivot" des montants selon les regles
    8. build_bank_summary     : ligne de synthese bancaire (ENC uniquement)
    9. apply_rounding_matrix  : calcul du Solde via la matrice d'arrondi
   10. add_group_keys         : cles de regroupement Group1 / Group2
   11. add_balancing_rows     : lignes d'ecart d'arrondi
   12. format_output          : formatage final des colonnes
   13. write_output           : ecriture .SUN et .csv
"""
import glob
import os
import re
import traceback
from datetime import datetime
from io import StringIO

import polars as pl


# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))        # .../Scripts/
BASE_FOLDER = os.path.dirname(SCRIPT_DIR)                      # racine du projet
SOURCE_FOLDER = os.path.join(BASE_FOLDER, "Brut")
DESTINATION_FOLDER = os.path.join(BASE_FOLDER, "Ready")
ERROR_FILE = os.path.join(SOURCE_FOLDER, "error.txt")
MAPPING_FILE = os.path.join(SCRIPT_DIR, "MatriceArrondiTakaful.csv")

SEUIL_POSITIF = 0.01
SEUIL_NEGATIF = -0.01

# Colonnes sources obligatoires (creees vides si absentes)
BASE_COLS = [
    "Code d'actes de Gestion", "Police", "Quittance", "Nom Assure", "Nom Contractant",
    "Date Effet", "Date emission", "Date Echeance", "Date envoi", "Date Reglement", "Date annulation",
    "ID Band", "quittance_nbr_repres", "Tiers", "code_produit",
]

# Colonnes du fichier de sortie, dans l'ordre
OUTPUT_COLS = [
    "CodeIFC", "NoPolice", "NoAdhesion", "NomAssure", "NomContractant", "DateEffet",
    "DateEmission", "DateEcheance", "DateEnvoi", "DateReglement", "DateRetour",
    "DateComptaSUNEmission", "DateComptaSUNAnnulation", "IDBand", "QuittanceNombreRepres",
    "DateTrxPeriod", "TrxDate", "TrxReference", "TrxDescription", "Agent", "Produit",
    "Support", "ChampLettrage", "Garantie", "CompteTakaful", "CritereCompte", "Montant",
    "Solde", "Group1", "Group2",
]


# ============================================================
# REGLES DE MAPPAGE
# ============================================================

# (prefixe colonne source, garantie, compte takaful)
GUARANTEES = [
    ("DECES", "G01", "CF01"),
    ("DTC",   "G07", "CF01"),
    ("IC",    "G02", "CG01"),
    ("DG",    "G03", "CG01"),
    ("BG",    "G04", "CG01"),
    ("EVCAT", "G05", "CG02"),
]

# (colonne source, suffixe du critere) -> en-tete "EQ"
DETAIL_SUFFIXES = [
    ("MT prime_TTC",            "PRIME_TTC"),
    ("MT prime_HT",             "PRIME_HT"),
    ("MT_taxe TSA",             "TAXE_TSA"),
    ("MT_taxe Parafiscale",     "TAXE_PARAFISC"),
    ("MT_chrg_gest",            "CHRG_GST"),
    ("MT_chrg_gest",            "CHRG_GST_CP"),
    ("MT_COMM TTC",             "COMM_TTC"),
    ("MT_COMM TTC",             "COMM_TTC_CP"),
]

# (colonne source, suffixe du critere) -> en-tete "ENC" (liberation commission)
LIB_COMM_SUFFIXES = [
    ("MT_COMM TTC",   "LIB_COMM_TTC"),
    ("MT_COMM",       "LIB_COMM_HT"),
    ("MT_taxe_comm",  "LIB_COMM_TAXE"),
]


def build_rules():
    """Regles de generation des lignes : (colonne, type d'en-tete, garantie, compte, pattern critere)."""
    rules = []
    for prefix, gar, cpt in GUARANTEES:
        for col, suffix in DETAIL_SUFFIXES:
            rules.append((f"{prefix} {col}", "EQ", gar, cpt, "{prefix}{code3}-" + suffix))
    for prefix, gar, cpt in GUARANTEES:
        for col, suffix in LIB_COMM_SUFFIXES:
            rules.append((f"{prefix} {col}", "ENC", gar, cpt, "{code03}-" + suffix))
    return rules


def build_payclient_rules():
    """Regles de reglement client (fichiers ENC uniquement)."""
    return [
        (f"{prefix} MT prime_TTC", "ENC", gar, cpt, "{code}-PRIME_TTC_CP")
        for prefix, gar, cpt in GUARANTEES
    ]


RULES = build_rules()
PAYCLIENT_RULES = build_payclient_rules()


# ============================================================
# UTILITAIRES
# ============================================================

def log_error(msg, exc_info=None):
    print(msg)
    msg_to_write = f"{msg}\n[Détails techniques] : {exc_info}" if exc_info else msg
    with open(ERROR_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} : {msg_to_write}\n")


def rel(path):
    return os.path.relpath(path, BASE_FOLDER)


def parse_dmy(col_name):
    """Expression Polars : colonne texte dd/mm/yyyy -> Date."""
    return pl.col(col_name).str.strptime(pl.Date, "%d/%m/%Y", strict=False)


def date_to_ddmmyyyy(col_name):
    return parse_dmy(col_name).dt.strftime("%d%m%Y").fill_null("")


def build_critere_expr(pattern):
    """Transforme un pattern '{prefix}{code3}-XXX' en expression Polars concatenee."""
    placeholders = {
        "prefix": pl.col("detail_prefix"),
        "code3": pl.col("code3"),
        "code03": pl.col("code03"),
        "code": pl.col("code"),
    }
    parts = []
    rest = pattern
    while rest:
        m = re.search(r"\{([^}]+)\}", rest)
        if not m:
            parts.append(pl.lit(rest))
            break
        if m.start() > 0:
            parts.append(pl.lit(rest[:m.start()]))
        key = m.group(1)
        if key in placeholders:
            parts.append(placeholders[key])
        rest = rest[m.end():]
    return pl.concat_str(parts)


def fmt_num(v):
    """Nombre -> texte avec 2 decimales max, sans zeros inutiles."""
    if v is None:
        return ""
    s = format(v, ".2f")
    return s.rstrip("0").rstrip(".") if "." in s else s


def is_code(prefix):
    """Expression : le code d'acte commence par `prefix`."""
    return pl.col("code").str.starts_with(prefix)


def by_file_type(enc_value, aq_value):
    """Expression : valeur selon le type de ligne (ENC / AQ), sinon vide."""
    return (
        pl.when(is_code("ENC")).then(enc_value)
        .when(is_code("AQ")).then(aq_value)
        .otherwise(pl.lit(""))
    )


# ============================================================
# ETAPE 0 : MATRICE D'ARRONDI
# ============================================================

def load_mapping():
    return pl.read_csv(MAPPING_FILE, separator=";", infer_schema_length=0).rename({"ID": "CritereCompte"})


# ============================================================
# ETAPES 1-2 : LECTURE ET NETTOYAGE
# ============================================================

def clean_source_text(file_path):
    """Replique des regex PowerShell : espaces, accents, virgules, 'null'."""
    with open(file_path, "r", encoding="latin-1", errors="ignore") as f:
        content = f.read()
    content = "\n".join(re.sub(r"\s+", " ", line) for line in content.splitlines())
    content = content.replace(" ;", ";").replace("è", "e").replace("é", "e").replace("ê", "e")
    content = content.replace(",", ";").replace("null;", ";").replace("NULL;", ";")
    return content


def load_source_df(content):
    """Tout en String pour ne pas perdre les zeros de tete."""
    return pl.read_csv(StringIO(content), separator=";", infer_schema_length=0, truncate_ragged_lines=True)


# ============================================================
# ETAPES 3-4 : TYPE DE FICHIER ET FILTRE
# ============================================================

def detect_file_type(df):
    """Retourne 'ENC', 'AQ' ou None si non reconnu."""
    first_code = df[0, "Code d'actes de Gestion"]
    if first_code and first_code.startswith("ENC"):
        return "ENC"
    if first_code and first_code.startswith("AQ"):
        return "AQ"
    return None


def filter_rows(df, file_type):
    if file_type == "ENC":
        return df.filter(pl.col("Date Reglement").str.len_chars() > 0)
    # AQ : uniquement les annulations de quittances payees (AQP...)
    return df.filter(pl.col("Code d'actes de Gestion").str.slice(2, 1) == "P")


# ============================================================
# ETAPE 5 : COLONNES REQUISES
# ============================================================

def ensure_base_columns(df):
    """Renomme les colonnes (insensible a la casse) et cree celles qui manquent."""
    rename_map = {}
    for col in df.columns:
        for bc in BASE_COLS:
            if col.lower().strip() == bc.lower().strip():
                rename_map[col] = bc
    df = df.rename(rename_map)
    missing = [pl.lit("").alias(c) for c in BASE_COLS if c not in df.columns]
    return df.with_columns(missing) if missing else df


# ============================================================
# ETAPE 6 : COLONNES DERIVEES
# ============================================================

def add_derived_columns(df):
    # Identifiants de base
    df = df.with_columns([
        pl.col("Code d'actes de Gestion").alias("code"),
        pl.col("Police").cast(pl.Int64, strict=False).cast(pl.Utf8).fill_null("").alias("police_int_str"),
        pl.col("Quittance").alias("quittance"),
        pl.col("Nom Assure").str.slice(0, 30).fill_null("").alias("nom_assure"),
        pl.col("Nom Contractant").str.slice(0, 30).fill_null("").alias("nom_contractant"),
        pl.col("Code d'actes de Gestion").str.slice(3).alias("code3"),
        pl.col("Code d'actes de Gestion").str.slice(0, 3).alias("code03"),
    ])

    # Prefixe de detail et date de transaction
    df = df.with_columns([
        by_file_type(pl.lit("EQ"), pl.lit("AQ")).alias("detail_prefix"),
        pl.when(is_code("ENC")).then(parse_dmy("Date Reglement"))
          .when(is_code("AQ")).then(parse_dmy("Date annulation"))
          .otherwise(pl.lit(None)).alias("trx_date_dt"),
    ])

    # Dates formatees, references et descriptions
    q = pl.col("quittance")
    suffix_ref = pl.col("code3") + "-" + q
    suffix_desc = pl.col("code3") + "- Quittance:" + q + "- Police:" + pl.col("Police")

    return df.with_columns([
        pl.col("trx_date_dt").dt.strftime("%d%m%Y").fill_null("").alias("trx_date"),
        (pl.lit("0") + pl.col("trx_date_dt").dt.strftime("%m%Y")).fill_null("").alias("trx_period"),

        date_to_ddmmyyyy("Date Effet").alias("eq_date_effet"),
        date_to_ddmmyyyy("Date emission").alias("eq_date_emission"),
        date_to_ddmmyyyy("Date Echeance").alias("eq_date_echeance"),
        date_to_ddmmyyyy("Date envoi").alias("eq_date_envoi"),
        date_to_ddmmyyyy("Date Reglement").alias("eq_date_reglement"),

        by_file_type(pl.lit("EQ") + suffix_ref,  pl.lit("AQ") + suffix_ref).alias("eq_trx_ref"),
        by_file_type(pl.lit("EQ") + suffix_desc, pl.lit("AQ") + suffix_desc).alias("eq_trx_desc"),
        by_file_type(pl.lit("ENC") + suffix_ref,  pl.lit("AENC") + suffix_ref).alias("enc_trx_ref"),
        by_file_type(pl.lit("ENC") + suffix_desc, pl.lit("AENC") + suffix_desc).alias("enc_trx_desc"),
    ])


# ============================================================
# ETAPE 7 : LIGNES DE DETAIL (UNPIVOT)
# ============================================================

def build_rule_lines(df, rule):
    """Genere les lignes d'ecriture pour UNE regle, ou None si rien a produire."""
    src_col, hdr_type, gar, cpt, crit_pat = rule
    if src_col not in df.columns:
        return None

    rule_df = df.filter(pl.col(src_col).is_not_null() & (pl.col(src_col) != "0.0"))
    if rule_df.height == 0:
        return None

    is_eq = hdr_type == "EQ"
    eq_or_blank = lambda col: pl.col(col) if is_eq else pl.lit("")

    return rule_df.select([
        pl.col("code").alias("CodeIFC"),
        pl.col("police_int_str").alias("NoPolice"),
        pl.col("quittance").alias("NoAdhesion"),
        pl.col("nom_assure").alias("NomAssure"),
        pl.col("nom_contractant").alias("NomContractant"),

        eq_or_blank("eq_date_effet").alias("DateEffet"),
        eq_or_blank("eq_date_emission").alias("DateEmission"),
        eq_or_blank("eq_date_echeance").alias("DateEcheance"),
        eq_or_blank("eq_date_envoi").alias("DateEnvoi"),
        eq_or_blank("eq_date_reglement").alias("DateReglement"),
        pl.lit("").alias("DateRetour"),
        pl.lit("").alias("DateComptaSUNEmission"),
        pl.lit("").alias("DateComptaSUNAnnulation"),

        pl.col("ID Band").cast(pl.Utf8).str.strip_chars().alias("IDBand"),
        pl.col("quittance_nbr_repres").alias("QuittanceNombreRepres"),
        pl.col("trx_period").alias("DateTrxPeriod"),
        pl.col("trx_date").alias("TrxDate"),

        (pl.col("eq_trx_ref") if is_eq else pl.col("enc_trx_ref")).alias("TrxReference"),
        (pl.col("eq_trx_desc") if is_eq else pl.col("enc_trx_desc")).alias("TrxDescription"),

        pl.col("Tiers").alias("Agent"),
        pl.col("code_produit").alias("Produit"),
        pl.lit("A00").alias("Support"),
        pl.col("quittance").alias("ChampLettrage"),

        pl.lit(gar).alias("Garantie"),
        pl.lit(cpt).alias("CompteTakaful"),
        build_critere_expr(crit_pat).alias("CritereCompte"),
        pl.col(src_col).alias("Montant"),
    ])


def build_detail_lines(df, file_type):
    rules = RULES + (PAYCLIENT_RULES if file_type == "ENC" else [])
    lines = (build_rule_lines(df, rule) for rule in rules)
    return [l for l in lines if l is not None]


# ============================================================
# ETAPE 8 : SYNTHESE BANCAIRE (ENC uniquement)
# ============================================================

def build_bank_summary(df):
    """Une ligne TTLBANQUE par (code, date de reglement). Retourne None si vide."""
    if "MT prime_TTC" not in df.columns:
        return None

    bank_df = df.filter(
        pl.col("MT prime_TTC").is_not_null()
        & (pl.col("MT prime_TTC") != "0.0")
        & (pl.col("MT prime_TTC") != "0")
    )
    if bank_df.height == 0:
        return None

    summary = (
        bank_df
        .with_columns(pl.col("MT prime_TTC").str.replace(",", ".").cast(pl.Float64, strict=False))
        .group_by(["code", "Date Reglement"])
        .agg(pl.col("MT prime_TTC").sum().round(2).alias("Somme"))
    )

    blank = lambda name: pl.lit("").alias(name)
    return summary.with_columns([
        date_to_ddmmyyyy("Date Reglement").alias("TrxDate"),
        (pl.lit("0") + parse_dmy("Date Reglement").dt.strftime("%m%Y")).fill_null("").alias("DateTrxPeriod"),
    ]).select([
        pl.col("code").alias("CodeIFC"), blank("NoPolice"), blank("NoAdhesion"),
        blank("NomAssure"), blank("NomContractant"), blank("DateEffet"),
        blank("DateEmission"), blank("DateEcheance"), blank("DateEnvoi"),
        pl.col("TrxDate").alias("DateReglement"), blank("DateRetour"), blank("DateComptaSUNEmission"),
        blank("DateComptaSUNAnnulation"), blank("IDBand"), blank("QuittanceNombreRepres"),
        pl.col("DateTrxPeriod"), pl.col("TrxDate"),
        (pl.col("code") + " " + pl.col("TrxDate")).alias("TrxReference"),
        (pl.col("code") + " " + pl.col("TrxDate")).alias("TrxDescription"),
        pl.lit("BF001").alias("Agent"), blank("Produit"), blank("Support"),
        blank("ChampLettrage"), blank("Garantie"), pl.lit("CG02").alias("CompteTakaful"),
        (pl.col("code") + "TTLBANQUE").alias("CritereCompte"),
        pl.col("Somme").cast(pl.Utf8).alias("Montant"),
    ])


# ============================================================
# ETAPE 9 : SOLDE VIA LA MATRICE D'ARRONDI
# ============================================================

def to_float_expr(col_name):
    return pl.col(col_name).cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64, strict=False).fill_null(0.0).round(2)


def apply_rounding_matrix(rnd_df, mapping_df):
    """Solde = Montant x signe (+1/-1) donne par la matrice."""
    rnd_df = rnd_df.join(mapping_df.select(["CritereCompte", "Data"]), on="CritereCompte", how="left")
    return rnd_df.with_columns([
        to_float_expr("Montant").alias("montant_num"),
        to_float_expr("Data").alias("data_num"),
    ]).with_columns(
        (pl.col("montant_num") * pl.col("data_num")).round(2).alias("Solde")
    )


# ============================================================
# ETAPE 10 : CLES DE REGROUPEMENT
# ============================================================

def add_group_keys(rnd_df):
    """Group1/Group2 : unite d'equilibre (quittance, encaissement banque, liberation commission)."""
    crit = pl.col("CritereCompte")
    ade = crit.is_in(["ENCADE-PRIME_TTC_CP", "ENCADETTLBANQUE"])
    mrb = crit.is_in(["ENCMRB-PRIME_TTC_CP", "ENCMRBTTLBANQUE"])
    lib = crit.str.slice(0, 12) == "ENC-LIB_COMM"
    eq = crit.str.slice(0, 2) == "EQ"

    return rnd_df.with_columns([
        pl.when(eq).then(pl.col("Garantie"))
          .when(ade).then(pl.lit("ENCADE"))
          .when(mrb).then(pl.lit("ENCMRB"))
          .when(lib).then(pl.lit("ENCLIBCOMM"))
          .otherwise(pl.lit("")).alias("Group1"),

        pl.when(eq).then(pl.col("NoAdhesion"))
          .when(ade | mrb | lib).then(pl.col("TrxDate"))
          .otherwise(pl.lit("")).alias("Group2"),
    ])


# ============================================================
# ETAPE 11 : LIGNES D'ECART D'ARRONDI
# ============================================================

def add_balancing_rows(rnd_df):
    """Ajoute une ligne de redressement par groupe dont le Solde total n'est pas nul."""
    diff_df = rnd_df.group_by(["Group1", "Group2"]).agg(pl.col("Solde").sum().round(2).alias("Difference"))
    rnd_df = rnd_df.join(diff_df, on=["Group1", "Group2"], how="left")

    diff_blocks = rnd_df.filter(pl.col("Difference").abs() > 0.0)
    if diff_blocks.height == 0:
        return rnd_df

    template_rows = diff_blocks.group_by(["Group1", "Group2"], maintain_order=True).first()
    diff = pl.col("Difference")
    base = pl.col("CritereCompte").str.slice(0, 2)

    balancing_rows = template_rows.with_columns([
        diff.abs().cast(pl.Utf8).alias("Montant"),
        (-diff).alias("Solde"),

        pl.when((diff <= SEUIL_POSITIF) & (diff > 0.0)).then(base + "-ECARTPOSITIF")
          .when((diff >= SEUIL_NEGATIF) & (diff < 0.0)).then(base + "-ECARTNEGATIF")
          .when(diff < SEUIL_NEGATIF).then(base + "-GRANDECARTN")
          .when(diff > SEUIL_POSITIF).then(base + "-GRANDECARTP")
          .otherwise(pl.col("CritereCompte")).alias("CritereCompte"),
    ]).select(rnd_df.columns)

    return pl.concat([rnd_df, balancing_rows], how="vertical")


# ============================================================
# ETAPE 12 : FORMATAGE FINAL
# ============================================================

def format_output(final_df):
    """Montant -> point (EN) | Solde -> virgule (FR)."""
    return final_df.with_columns([
        pl.col("Montant").cast(pl.Utf8).str.replace(",", ".").alias("Montant"),
        pl.col("Solde").cast(pl.Float64, strict=False)
          .map_elements(lambda v: fmt_num(v).replace(".", ","), return_dtype=pl.Utf8)
          .alias("Solde"),
    ]).select(OUTPUT_COLS)


# ============================================================
# ETAPE 13 : ECRITURE
# ============================================================

def write_output(final_df, file_path):
    """ASCII, CRLF, sans ligne vide finale (rejetee par l'outil d'upload)."""
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    sun_path = os.path.join(DESTINATION_FOLDER, f"{base_name}.SUN")
    csv_path = os.path.join(DESTINATION_FOLDER, f"{base_name}.csv")

    content = final_df.write_csv(separator=";", quote_style="never", line_terminator="\r\n")
    content = content.rstrip("\r\n")

    for out_path in (sun_path, csv_path):
        with open(out_path, "w", encoding="ascii", errors="ignore", newline="") as f:
            f.write(content)

    print(f"Fichiers générés : {rel(sun_path)} et {rel(csv_path)}")


# ============================================================
# ORCHESTRATION
# ============================================================

def process_file(file_path, mapping_df):
    """Traite un fichier brut de bout en bout. Ne fait rien si le fichier est vide/ignore."""
    print(f"Préparation du fichier : {rel(file_path)} : Phase 1.")

    df = load_source_df(clean_source_text(file_path))
    if df.height == 0:
        return

    file_type = detect_file_type(df)
    if file_type is None:
        print(f"Fichier ignoré car code non reconnu: {df[0, 'Code d' + chr(39) + 'actes de Gestion']}")
        return

    df = filter_rows(df, file_type)
    if df.height == 0:
        return

    print(f"Préparation du fichier : {rel(file_path)} : Phase 2.")

    df = ensure_base_columns(df)
    df = add_derived_columns(df)

    output_dfs = build_detail_lines(df, file_type)
    if file_type == "ENC":
        bank = build_bank_summary(df)
        if bank is not None:
            output_dfs.append(bank)
    if not output_dfs:
        return

    rnd_df = pl.concat(output_dfs, how="vertical")
    rnd_df = apply_rounding_matrix(rnd_df, mapping_df)
    rnd_df = add_group_keys(rnd_df)
    final_df = add_balancing_rows(rnd_df)

    write_output(format_output(final_df), file_path)


def process_files():
    try:
        mapping_df = load_mapping()
    except Exception as e:
        log_error(f"Erreur chargement matrice d'arrondi : {str(e)}", exc_info=traceback.format_exc())
        return

    for file_path in glob.glob(os.path.join(SOURCE_FOLDER, "*.csv")):
        if os.path.isdir(file_path) or file_path in (MAPPING_FILE, ERROR_FILE):
            continue
        try:
            process_file(file_path, mapping_df)
        except Exception as e:
            log_error(f"Erreur lors du traitement de {file_path} : {str(e)}", exc_info=traceback.format_exc())


if __name__ == "__main__":
    process_files()
