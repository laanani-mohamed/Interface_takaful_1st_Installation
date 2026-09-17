import polars as pl
import os
import glob
import re
from io import StringIO
from datetime import datetime
import traceback


SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))                   # .../Scripts/
BASE_FOLDER  = os.path.dirname(SCRIPT_DIR)                 # .../Interface_takaful-main/
SOURCE_FOLDER      = os.path.join(BASE_FOLDER, "Brut")                      # .../Brut/
DESTINATION_FOLDER = os.path.join(BASE_FOLDER, "Ready")                     # .../Ready/
ERROR_FILE         = os.path.join(SOURCE_FOLDER, "error.txt")               # .../Brut/error.txt
MAPPING_FILE       = os.path.join(SCRIPT_DIR, "MatriceArrondiTakaful.csv")  # .../Scripts/MatriceArrondiTakaful.csv


# MAPPAGE DES RÈGLES

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


# UTILITAIRES

def log_error(msg, exc_info=None):
    print(msg)
    if exc_info:
        msg_to_write = f"{msg}\n[Détails techniques] : {exc_info}"
    else:
        msg_to_write = msg
    with open(ERROR_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now()} : {msg_to_write}\n")

def parse_dmy(col_name):
    return pl.col(col_name).str.strptime(pl.Date, "%d/%m/%Y", strict=False)

def build_critere_expr(pattern):
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
        if key == "prefix": parts.append(pl.col("detail_prefix"))
        elif key == "code3": parts.append(pl.col("code3"))
        elif key == "code03": parts.append(pl.col("code03"))
        elif key == "code": parts.append(pl.col("code"))
            
        rest = rest[m.end():]
    return pl.concat_str(parts)


# TRAITEMENT PRINCIPAL

def process_files():
    try:
        mapping_df = pl.read_csv(MAPPING_FILE, separator=";", infer_schema_length=0).rename({"ID": "CritereCompte"})
    except Exception as e:
        log_error(f"Erreur chargement matrice d'arrondi : {str(e)}", exc_info=traceback.format_exc())
        return

    search_pattern = os.path.join(SOURCE_FOLDER, "*.csv")
    for file_path in glob.glob(search_pattern):
        if os.path.isdir(file_path) or file_path in [MAPPING_FILE, ERROR_FILE]:
            continue
            
        print(f"Préparation du fichier : {os.path.relpath(file_path, BASE_FOLDER)} : Phase 1.")
        try:
            # 1. Nettoyage syntaxique du texte (réplique exacte des Regex PS1)
            with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                content = f.read()
                
            # Simulate Get-Content (line by line) replacement of spaces
            content = '\n'.join([re.sub(r'\s+', ' ', line) for line in content.splitlines()])
            content = content.replace(' ;', ';').replace('è', 'e').replace('é', 'e').replace('ê', 'e')
            content = content.replace(',', ';').replace('null;', ';').replace('NULL;', ';')
            
            # 2. Lecture Polars avec tout forcé en String pour éviter les pertes de zéros
            df = pl.read_csv(StringIO(content), separator=";", infer_schema_length=0, truncate_ragged_lines=True)
            
            if df.height == 0:
                continue
                
            first_code = df[0, "Code d'actes de Gestion"]
            is_enc_file = first_code.startswith("ENC") if first_code else False
            is_aq_file = first_code.startswith("AQ") if first_code else False
            
            # Application du filtre principal selon le type de fichier
            if is_enc_file:
                df = df.filter(pl.col("Date Reglement").str.len_chars() > 0)
            elif is_aq_file:
                df = df.filter(pl.col("Code d'actes de Gestion").str.slice(2, 1) == "P")
            else:
                print(f"Fichier ignoré car code non reconnu: {first_code}")
                continue
            
            if df.height == 0:
                continue
                
            print(f"Préparation du fichier : {os.path.relpath(file_path, BASE_FOLDER)} : Phase 2.")
            
            # Sécurisation des colonnes requises
            base_cols = [
                "Code d'actes de Gestion", "Police", "Quittance", "Nom Assure", "Nom Contractant",
                "Date Effet", "Date emission", "Date Echeance", "Date envoi", "Date Reglement", "Date annulation",
                "ID Band", "quittance_nbr_repres", "Tiers", "code_produit"
            ]
            
            # Rename columns case-insensitively like PowerShell
            rename_map = {}
            for col in df.columns:
                for bc in base_cols:
                    if col.lower().strip() == bc.lower().strip():
                        rename_map[col] = bc
            df = df.rename(rename_map)
            for c in base_cols:
                if c not in df.columns:
                    df = df.with_columns(pl.lit("").alias(c))

            # Création des colonnes dérivées
            df = df.with_columns([
                pl.col("Code d'actes de Gestion").alias("code"),
                pl.col("Police").cast(pl.Int64, strict=False).cast(pl.Utf8).fill_null("").alias("police_int_str"),
                pl.col("Quittance").alias("quittance"),
                pl.col("Nom Assure").str.slice(0, 30).fill_null("").alias("nom_assure"),
                pl.col("Nom Contractant").str.slice(0, 30).fill_null("").alias("nom_contractant"),
                pl.col("Code d'actes de Gestion").str.slice(3).alias("code3"),
                pl.col("Code d'actes de Gestion").str.slice(0, 3).alias("code03"),
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

            output_dfs = []
            all_rules = RULES.copy()
            if is_enc_file:
                all_rules.extend(PAYCLIENT_RULES)
                
            # Boucle d'unpivot (Melt manuel)
            for src_col, hdr_type, gar, cpt, crit_pat in all_rules:
                if src_col not in df.columns:
                    continue
                    
                rule_df = df.filter((pl.col(src_col).is_not_null()) & (pl.col(src_col) != "0.0"))
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
                
            # Ligne de résumé bancaire (IFCSummaryPayBanque)
            if is_enc_file and "MT prime_TTC" in df.columns:
                bank_df = df.filter((pl.col("MT prime_TTC").is_not_null()) & (pl.col("MT prime_TTC") != "0.0") & (pl.col("MT prime_TTC") != "0"))
                if bank_df.height > 0:
                    bank_summary = bank_df.with_columns(
                        pl.col("MT prime_TTC").str.replace(",", ".").cast(pl.Float64, strict=False)
                    ).group_by(["code", "Date Reglement"]).agg(
                        pl.col("MT prime_TTC").sum().round(2).alias("Somme")
                    )
                    
                    bank_sel = bank_summary.with_columns([
                        parse_dmy("Date Reglement").dt.strftime("%d%m%Y").fill_null("").alias("TrxDate"),
                        (pl.lit("0") + parse_dmy("Date Reglement").dt.strftime("%m%Y")).fill_null("").alias("DateTrxPeriod")
                    ]).select([
                        pl.col("code").alias("CodeIFC"), pl.lit("").alias("NoPolice"), pl.lit("").alias("NoAdhesion"),
                        pl.lit("").alias("NomAssure"), pl.lit("").alias("NomContractant"), pl.lit("").alias("DateEffet"),
                        pl.lit("").alias("DateEmission"), pl.lit("").alias("DateEcheance"), pl.lit("").alias("DateEnvoi"),
                        pl.col("TrxDate").alias("DateReglement"), pl.lit("").alias("DateRetour"), pl.lit("").alias("DateComptaSUNEmission"),
                        pl.lit("").alias("DateComptaSUNAnnulation"), pl.lit("").alias("IDBand"), pl.lit("").alias("QuittanceNombreRepres"),
                        pl.col("DateTrxPeriod"), pl.col("TrxDate"),
                        (pl.col("code") + " " + pl.col("TrxDate")).alias("TrxReference"),
                        (pl.col("code") + " " + pl.col("TrxDate")).alias("TrxDescription"),
                        pl.lit("BF001").alias("Agent"), pl.lit("").alias("Produit"), pl.lit("").alias("Support"),
                        pl.lit("").alias("ChampLettrage"), pl.lit("").alias("Garantie"), pl.lit("CG02").alias("CompteTakaful"),
                        (pl.col("code") + "TTLBANQUE").alias("CritereCompte"),
                        pl.col("Somme").cast(pl.Utf8).alias("Montant")
                    ])
                    output_dfs.append(bank_sel)

            if not output_dfs:
                continue
                
            # Concaténation de toutes les écritures générées (Equivalent du fichier .RND)
            rnd_df = pl.concat(output_dfs, how="vertical")
            
            # Phase 2: Traitement des écarts d'arrondi
            rnd_df = rnd_df.join(mapping_df.select(["CritereCompte", "Data"]), on="CritereCompte", how="left")
            
            # Calcul du Solde
            rnd_df = rnd_df.with_columns([
                pl.col("Montant").cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64, strict=False).fill_null(0.0).round(2).alias("montant_num"),
                pl.col("Data").cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64, strict=False).fill_null(0.0).round(2).alias("data_num")
            ]).with_columns(
                (pl.col("montant_num") * pl.col("data_num")).round(2).alias("Solde")
            )
            
            # Construction des clés de lettrage Group1 / Group2 (Réplique exacte PS1 hardcodée)
            rnd_df = rnd_df.with_columns([
                pl.when(pl.col("CritereCompte").str.slice(0, 2) == "EQ").then(pl.col("Garantie"))
                  .when(pl.col("CritereCompte").is_in(["ENCADE-PRIME_TTC_CP", "ENCADETTLBANQUE"])).then(pl.lit("ENCADE"))
                  .when(pl.col("CritereCompte").is_in(["ENCMRB-PRIME_TTC_CP", "ENCMRBTTLBANQUE"])).then(pl.lit("ENCMRB"))
                  .when(pl.col("CritereCompte").str.slice(0, 12) == "ENC-LIB_COMM").then(pl.lit("ENCLIBCOMM"))
                  .otherwise(pl.lit("")).alias("Group1"),
                  
                pl.when(pl.col("CritereCompte").str.slice(0, 2) == "EQ").then(pl.col("NoAdhesion"))
                  .when(pl.col("CritereCompte").is_in(["ENCADE-PRIME_TTC_CP", "ENCADETTLBANQUE"])).then(pl.col("TrxDate"))
                  .when(pl.col("CritereCompte").is_in(["ENCMRB-PRIME_TTC_CP", "ENCMRBTTLBANQUE"])).then(pl.col("TrxDate"))
                  .when(pl.col("CritereCompte").str.slice(0, 12) == "ENC-LIB_COMM").then(pl.col("TrxDate"))
                  .otherwise(pl.lit("")).alias("Group2"),
            ])
            
            diff_df = rnd_df.group_by(["Group1", "Group2"]).agg([
                pl.col("Solde").sum().round(2).alias("Difference")
            ])
            
            rnd_df = rnd_df.join(diff_df, on=["Group1", "Group2"], how="left")
            diff_blocks = rnd_df.filter(pl.col("Difference").abs() > 0.0)
            
            if diff_blocks.height > 0:
                # Création des lignes de redressement / centimes d'arrondis
                template_rows = diff_blocks.group_by(["Group1", "Group2"], maintain_order=True).first()
                
                SEUIL_POSITIF = 0.01
                SEUIL_NEGATIF = -0.01
                
                balancing_rows = template_rows.with_columns([
                    pl.col("Difference").abs().cast(pl.Utf8).alias("Montant"),
                    (-pl.col("Difference")).alias("Solde"),
                    
                    pl.when((pl.col("Difference") <= SEUIL_POSITIF) & (pl.col("Difference") > 0.0))
                      .then(pl.col("CritereCompte").str.slice(0, 2) + "-ECARTPOSITIF")
                      .when((pl.col("Difference") >= SEUIL_NEGATIF) & (pl.col("Difference") < 0.0))
                      .then(pl.col("CritereCompte").str.slice(0, 2) + "-ECARTNEGATIF")
                      .when(pl.col("Difference") < SEUIL_NEGATIF)
                      .then(pl.col("CritereCompte").str.slice(0, 2) + "-GRANDECARTN")
                      .when(pl.col("Difference") > SEUIL_POSITIF)
                      .then(pl.col("CritereCompte").str.slice(0, 2) + "-GRANDECARTP")
                      .otherwise(pl.col("CritereCompte")).alias("CritereCompte")
                ]).select(rnd_df.columns)
                
                final_df = pl.concat([rnd_df, balancing_rows], how="vertical")
            else:
                final_df = rnd_df
                
            columns_to_export = [
                "CodeIFC", "NoPolice", "NoAdhesion", "NomAssure", "NomContractant", "DateEffet", 
                "DateEmission", "DateEcheance", "DateEnvoi", "DateReglement", "DateRetour", 
                "DateComptaSUNEmission", "DateComptaSUNAnnulation", "IDBand", "QuittanceNombreRepres", 
                "DateTrxPeriod", "TrxDate", "TrxReference", "TrxDescription", "Agent", "Produit", 
                "Support", "ChampLettrage", "Garantie", "CompteTakaful", "CritereCompte", "Montant",
                "Solde", "Group1", "Group2"
            ]
            
            # Fonction de formatage précis pour éviter l'arrondi scientifique/significatif de f"{v:g}"
            def fmt_num(v):
                if v is None: return ""
                s = format(v, ".2f")
                return s.rstrip("0").rstrip(".") if "." in s else s

            # Montant → point "." (format EN) | Solde → virgule "," (format FR)
            final_df = final_df.with_columns([
                pl.col("Montant").cast(pl.Utf8)
                    .str.replace(",", ".")
                    .alias("Montant"),
                pl.col("Solde")
                    .cast(pl.Float64, strict=False)
                    .map_elements(lambda v: fmt_num(v).replace(".", ","), return_dtype=pl.Utf8)
                    .alias("Solde")
            ]).select(columns_to_export)
            
            # Sauvegarde au format final SUN et CSV
            # Encodage ASCII (comme PowerShell Export-Csv -Encoding ASCII)
            # Fins de ligne CRLF \r\n (Windows)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            sun_path = os.path.join(DESTINATION_FOLDER, f"{base_name}.SUN")
            csv_path = os.path.join(DESTINATION_FOLDER, f"{base_name}.csv")

            # Générer le contenu CSV avec séparateur \r\n (CRLF)
            csv_content = final_df.write_csv(separator=";", quote_style="never", line_terminator="\r\n")

            # Supprimer le \r\n final pour éviter la ligne vide en fin de fichier
            # (le logiciel d'upload rejette les fichiers avec ligne vide finale)
            csv_content = csv_content.rstrip("\r\n")

            # Écrire en ASCII — newline="" pour ne pas doubler les \r\n
            for out_path in (sun_path, csv_path):
                with open(out_path, "w", encoding="ascii", errors="ignore", newline="") as f:
                    f.write(csv_content)

            print(f"Fichiers générés : {os.path.relpath(sun_path, BASE_FOLDER)} et {os.path.relpath(csv_path, BASE_FOLDER)}")
            
        except Exception as e:
            log_error(f"Erreur lors du traitement de {file_path} : {str(e)}", exc_info=traceback.format_exc())

if __name__ == '__main__':
    process_files()
