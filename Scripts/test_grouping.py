import polars as pl
import os
import glob
from Interface_Takaful import RULES, PAYCLIENT_RULES, parse_dmy, build_critere_expr

def run_test():
    # Load raw
    df = pl.read_csv("Brut/Encaissement_13-05-2026_17_09.csv", separator=";", infer_schema_length=10000)
    df = df.with_row_index("_row_idx")
    mapping_df = pl.read_csv("Scripts/MatriceArrondiTakaful.csv", separator=";")
    
    # Simple melt
    output_dfs = []
    all_rules = RULES.copy()
    all_rules.extend(PAYCLIENT_RULES)
    for i, (src_col, hdr_type, gar, cpt, crit_pat) in enumerate(all_rules):
        if src_col not in df.columns: continue
        rule_df = df.filter((pl.col(src_col).is_not_null()) & (pl.col(src_col) != "0.0") & (pl.col(src_col) != "0"))
        if rule_df.height == 0: continue
        sel = rule_df.select([
            pl.col("code").alias("CodeIFC"), pl.lit("").alias("NoPolice"), pl.col("quittance").alias("NoAdhesion"),
            pl.lit("").alias("NomAssure"), pl.lit("").alias("NomContractant"), pl.lit("").alias("DateEffet"),
            pl.lit("").alias("DateEmission"), pl.lit("").alias("DateEcheance"), pl.lit("").alias("DateEnvoi"),
            pl.col("eq_date_reglement").alias("DateReglement"), pl.lit("").alias("DateRetour"), pl.lit("").alias("DateComptaSUNEmission"),
            pl.lit("").alias("DateComptaSUNAnnulation"), pl.lit("").alias("IDBand"), pl.lit("").alias("QuittanceNombreRepres"),
            pl.col("trx_period").alias("DateTrxPeriod"), pl.col("trx_date").alias("TrxDate"), pl.col("enc_trx_ref").alias("TrxReference"),
            pl.col("enc_trx_desc").alias("TrxDescription"), pl.lit("BF001").alias("Agent"), pl.lit("").alias("Produit"),
            pl.lit("A00").alias("Support"), pl.col("quittance").alias("ChampLettrage"), pl.lit(gar).alias("Garantie"),
            pl.lit(cpt).alias("CompteTakaful"), build_critere_expr(crit_pat).alias("CritereCompte"), pl.col(src_col).alias("Montant"),
            pl.col("_row_idx"), pl.lit(i).alias("_rule_idx")
        ])
        output_dfs.append(sel)
        
    bank_df = df.filter((pl.col("MT prime_TTC").is_not_null()) & (pl.col("MT prime_TTC") != "0.0") & (pl.col("MT prime_TTC") != "0"))
    if bank_df.height > 0:
        bank_summary = bank_df.with_columns(
            pl.col("MT prime_TTC").str.replace(",", ".").cast(pl.Float64, strict=False)
        ).group_by(["code", "Date Reglement"]).agg([
            pl.col("MT prime_TTC").sum().round(2).alias("Somme"),
            pl.col("_row_idx").first().alias("_row_idx")
        ])
        bank_sel = bank_summary.with_columns([
            parse_dmy("Date Reglement").dt.strftime("%d%m%Y").fill_null("").alias("TrxDate"),
            (pl.lit("0") + parse_dmy("Date Reglement").dt.strftime("%m%Y")).fill_null("").alias("DateTrxPeriod")
        ]).select([
            pl.col("code").alias("CodeIFC"), pl.lit("").alias("NoPolice"), pl.lit("").alias("NoAdhesion"),
            pl.lit("").alias("NomAssure"), pl.lit("").alias("NomContractant"), pl.lit("").alias("DateEffet"),
            pl.lit("").alias("DateEmission"), pl.lit("").alias("DateEcheance"), pl.lit("").alias("DateEnvoi"),
            pl.col("TrxDate").alias("DateReglement"), pl.lit("").alias("DateRetour"), pl.lit("").alias("DateComptaSUNEmission"),
            pl.lit("").alias("DateComptaSUNAnnulation"), pl.lit("").alias("IDBand"), pl.lit("").alias("QuittanceNombreRepres"),
            pl.col("DateTrxPeriod"), pl.col("TrxDate"), (pl.col("code") + " " + pl.col("TrxDate")).alias("TrxReference"),
            (pl.col("code") + " " + pl.col("TrxDate")).alias("TrxDescription"), pl.lit("BF001").alias("Agent"),
            pl.lit("").alias("Produit"), pl.lit("").alias("Support"), pl.lit("").alias("ChampLettrage"), pl.lit("").alias("Garantie"),
            pl.lit("CG02").alias("CompteTakaful"), (pl.col("code") + "TTLBANQUE").alias("CritereCompte"),
            pl.col("Somme").cast(pl.Utf8).alias("Montant"), pl.col("_row_idx"), pl.lit(999).alias("_rule_idx")
        ])
        output_dfs.append(bank_sel)

    rnd_df = pl.concat(output_dfs, how="vertical")
    
    # 1. Obtenir CREData dans le même ordre que PS1
    rnd_df = rnd_df.sort(["_row_idx", "_rule_idx"])
    rnd_df = rnd_df.drop(["_row_idx", "_rule_idx"])
    
    # Phase 2
    rnd_df = rnd_df.join(mapping_df.select(["CritereCompte", "Data"]), on="CritereCompte", how="left")
    rnd_df = rnd_df.with_columns([
        pl.col("Montant").cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64, strict=False).round(2).alias("montant_num"),
        pl.col("Data").cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64, strict=False).round(2).alias("data_num")
    ]).with_columns((pl.col("montant_num") * pl.col("data_num")).alias("Solde"))
    
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
    
    # 2. Trouver l'ordre des groupes (Group-Object maintain_order)
    group_order = rnd_df.select(["Group1", "Group2"]).unique(maintain_order=True).with_row_index("group_id")
    
    # 3. Assigner cet ID et _pos pour garder l'ordre interne du groupe
    rnd_df = rnd_df.join(group_order, on=["Group1", "Group2"], how="left")
    rnd_df = rnd_df.with_row_index("_internal_pos")
    
    # 4. Tri final bloc par bloc
    rnd_df = rnd_df.sort(["group_id", "_internal_pos"])
    
    diff_df = rnd_df.group_by(["Group1", "Group2"]).agg([
        pl.col("Solde").sum().round(2).alias("Difference")
    ])
    
    rnd_df = rnd_df.join(diff_df, on=["Group1", "Group2"], how="left")
    diff_blocks = rnd_df.filter(pl.col("Difference").abs() > 0.0)
    
    if diff_blocks.height > 0:
        template_rows = diff_blocks.group_by(["Group1", "Group2"], maintain_order=True).first()
        balancing_rows = template_rows.with_columns([
            pl.col("Difference").abs().cast(pl.Utf8).alias("Montant"),
            (-pl.col("Difference")).alias("Solde"),
            pl.when((pl.col("Difference") <= 0.01) & (pl.col("Difference") > 0.0))
              .then(pl.col("CritereCompte").str.slice(0, 2) + "-ECARTPOSITIF")
              .when((pl.col("Difference") >= -0.01) & (pl.col("Difference") < 0.0))
              .then(pl.col("CritereCompte").str.slice(0, 2) + "-ECARTNEGATIF")
              .when(pl.col("Difference") < -0.01)
              .then(pl.col("CritereCompte").str.slice(0, 2) + "-GRANDECARTN")
              .when(pl.col("Difference") > 0.01)
              .then(pl.col("CritereCompte").str.slice(0, 2) + "-GRANDECARTP")
              .otherwise(pl.col("CritereCompte")).alias("CritereCompte")
        ]).select(rnd_df.columns)
        
        group_end_pos = rnd_df.filter(pl.col("Difference").abs() > 0.0).group_by(["group_id"]).agg(pl.col("_internal_pos").max().alias("_group_end_pos"))
        rnd_df = rnd_df.with_columns(pl.col("_internal_pos").cast(pl.Float64).alias("_sort_pos"))
        balancing_rows = balancing_rows.join(group_end_pos, on=["group_id"], how="left").with_columns(
            (pl.col("_group_end_pos").cast(pl.Float64) + 0.5).alias("_sort_pos")
        ).drop("_group_end_pos")
        
        final_df = pl.concat([rnd_df, balancing_rows], how="diagonal").sort(["group_id", "_sort_pos"]).drop(["_internal_pos", "_sort_pos", "group_id"])
    else:
        final_df = rnd_df.drop(["_internal_pos", "group_id"])
        
    print(f"Final output height: {final_df.height}")
    import pandas as pd
    df_pd = final_df.to_pandas()
    df_pd['Group_Key'] = df_pd['Group1'] + '-' + df_pd['Group2']
    groups = df_pd['Group_Key'].tolist()
    non_adjacent = 0
    seen = set()
    last_group = None
    for g in groups:
        if pd.isna(g): continue
        if g != last_group:
            if g in seen:
                non_adjacent += 1
            seen.add(g)
            last_group = g
    print(f'Non-adjacent groups: {non_adjacent}')
    balancing = df_pd[df_pd['CritereCompte'].str.contains('ECART', na=False)]
    print(f'Balancing rows found: {len(balancing)}')

if __name__ == "__main__":
    run_test()
