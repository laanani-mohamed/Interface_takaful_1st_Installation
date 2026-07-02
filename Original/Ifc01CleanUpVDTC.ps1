$baseFolder            ="C:\Temp\"
$sourceFolder          =$baseFolder + "Brut\"
$tempDestinationFolder =$baseFolder + "Ready\"
$destinationFolder     =$baseFolder + "Ready\"
$originalFolder        =$baseFolder + "Brut\Original\"
$errorFile             =$baseFolder + "error.txt"
$csvFile               =""
$NoEnregistrement      = 1
$dateTimeFormatSource  ='dd/MM/yyyy'
$ZERO                 ="0.0"


##################variables pour la gestion des arrondis ##############
$SeuilPositif                   =0.01

$SeuilNegatif                   =-0.01
$CritereAdditionnelSeuilPositif ="ECARTPOSITIF"
$CritereAdditionnelSeuilNegatif ="ECARTNEGATIF"
$CritereAdditionnelGRANDECARTP  ="GRANDECARTP"
$CritereAdditionnelGRANDECARTN  ="GRANDECARTN"
$mappingFile                    =$baseFolder + "\Scripts\MatriceArrondiTakaful.csv"
$Separateur                     =";"

#######################################################################

function IFCHeaderEQ($row)
{
        if($row.'Code d''actes de Gestion'.Substring(0,3) -eq "ENC")
        {
              $TrxDate        = ([Datetime]::ParseExact($row."Date Reglement"   , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')          
              $TrxPeriod      ="0" + ([Datetime]::ParseExact($row."Date Reglement"   , $dateTimeFormatSource ,$null)).ToString('MMyyyy')
              $trxReference   = "EQ" + $row."Code d'actes de Gestion".SubString(3,$row."Code d'actes de Gestion".Length-3) + "-"+$row.Quittance
              $trxDescription = "EQ" + $row."Code d'actes de Gestion".SubString(3,$row."Code d'actes de Gestion".Length-3) + "- Quittance:"+$row.Quittance + "- Police:"+$row.Police

        }
        if($row.'Code d''actes de Gestion'.Substring(0,2) -eq "AQ")
        {
              $TrxDate        = ([Datetime]::ParseExact($row."Date annulation"   , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')          
              $TrxPeriod      ="0" + ([Datetime]::ParseExact($row."Date annulation"   , $dateTimeFormatSource ,$null)).ToString('MMyyyy')
              $trxReference   = "AQ" + $row."Code d'actes de Gestion".SubString(3,$row."Code d'actes de Gestion".Length-3) + "-"+$row.Quittance
              $trxDescription = "AQ" + $row."Code d'actes de Gestion".SubString(3,$row."Code d'actes de Gestion".Length-3) + "- Quittance:"+$row.Quittance + "- Police:"+$row.Police

        }

            

           if($row.'Date Effet'.Length -gt 0 )
            {
                $DateEffet       = ([Datetime]::ParseExact($row."Date Effet"                 , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
            }
          

         if($row.'Date emission'.Length -gt 0 )
            {
          $DateEmission    = ([Datetime]::ParseExact($row."Date emission"              , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
          }

          
           if($row.'Date Echeance'.Length -gt 0 )
            {
          $DateEcheance    = ([Datetime]::ParseExact($row."Date Echeance"              , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
          }
          if($row.'Date envoi'.Length -gt 0 )
            {
          $DateEnvoi       = ([Datetime]::ParseExact($row."Date envoi"                 , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
            }
            if($row.'Date Reglement'.Length -gt 0 )
            {                      
            $DateReglement   = ([Datetime]::ParseExact($row."Date Reglement"             , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
            }
          $DateRetour      = ""
          ##([Datetime]::ParseExact($row."Date retour"                , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
          $DateCompta      = ""
          ##([Datetime]::ParseExact($row."Date compta SUN Emission"   , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
          $DateComptaAnnul = ""
          ##([Datetime]::ParseExact($row."Date compta SUN Annulation" , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')

          $NomAssure      = $row."Nom Assure"
          $NomContractant = $row."Nom Contractant"
          if ($NomAssure.Length -gt 30) { $NomAssure = $row."Nom Assure".Substring(0,30)}
          if ($NomContractant.Length -gt 30) { $NomContractant = $row."Nom Contractant".Substring(0,30)}

          $NoPolice = [int]::Parse($row."Police")

          $result = $row."Code d'actes de Gestion" + ";" + $NoPolice + ";" + $row."Quittance" +";" + $NomAssure + ";" + $NomContractant + ";" + $DateEffet +";" + $DateEmission
          $result = $result + ";"+ $DateEcheance + ";" + $DateEnvoi +";" +$DateReglement +";" +$DateRetour +";"+$DateCompta +";" +$DateComptaAnnul +";" 
          $result = $result + $row."ID Band" +";"+ $row."quittance_nbr_repres" +";" +$TrxPeriod + ";" + $TrxDate +";" + $trxReference + ";" +$trxDescription +";" +$row.Tiers + ";" +$row.code_produit + ";A00;" + $row.Quittance +";"
          
          return $result
}

function IFCHeaderENC($row)
{
            if($row.'Code d''actes de Gestion'.Substring(0,3) -eq "ENC")
            {
              $TrxDate        = ([Datetime]::ParseExact($row."Date Reglement"   , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')          
              $TrxPeriod      ="0" + ([Datetime]::ParseExact($row."Date Reglement"   , $dateTimeFormatSource ,$null)).ToString('MMyyyy')
              $trxReference   = "ENC" + $row."Code d'actes de Gestion".SubString(3,$row."Code d'actes de Gestion".Length-3) + "-"+$row.Quittance
              $trxDescription = "ENC" + $row."Code d'actes de Gestion".SubString(3,$row."Code d'actes de Gestion".Length-3) + "- Quittance:"+$row.Quittance + "- Police:"+$row.Police

            }
            if($row.'Code d''actes de Gestion'.Substring(0,2) -eq "AQ")
            {
              $TrxDate        = ([Datetime]::ParseExact($row."Date annulation"   , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')          
              $TrxPeriod      ="0" + ([Datetime]::ParseExact($row."Date annulation"   , $dateTimeFormatSource ,$null)).ToString('MMyyyy')
              $trxReference   = "AENC" + $row."Code d'actes de Gestion".SubString(3,$row."Code d'actes de Gestion".Length-3) + "-"+$row.Quittance
              $trxDescription = "AENC" + $row."Code d'actes de Gestion".SubString(3,$row."Code d'actes de Gestion".Length-3) + "- Quittance:"+$row.Quittance + "- Police:"+$row.Police

            }


      #   $TrxDate        = ([Datetime]::ParseExact($row."Date Reglement"   , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
      #   $TrxPeriod      ="0" + ([Datetime]::ParseExact($row."Date Reglement"   , $dateTimeFormatSource ,$null)).ToString('MMyyyy')

          $DateEffet       =  ""
#([Datetime]::ParseExact($row."Date Effet"                 , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
          $DateEmission    =  ""
#([Datetime]::ParseExact($row."Date emission"              , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
          $DateEcheance    =  ""
#([Datetime]::ParseExact($row."Date Echeance"              , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
          $DateEnvoi       =  ""
#([Datetime]::ParseExact($row."Date envoi"                 , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
          $DateReglement   =  ""
#([Datetime]::ParseExact($row."Date Reglement"             , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
          $DateRetour      = ""
          ##([Datetime]::ParseExact($row."Date retour"                , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
          $DateCompta      = ""
          ##([Datetime]::ParseExact($row."Date compta SUN Emission"   , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
          $DateComptaAnnul = ""
          ##([Datetime]::ParseExact($row."Date compta SUN Annulation" , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')

          $NomAssure      = $row."Nom Assure"
          $NomContractant = $row."Nom Contractant"
          if ($NomAssure.Length -gt 30) { $NomAssure = $row."Nom Assure".Substring(0,30)}
          if ($NomContractant.Length -gt 30) { $NomContractant = $row."Nom Contractant".Substring(0,30)}

          $NoPolice = [int]::Parse($row."Police")

          $result = $row."Code d'actes de Gestion" + ";" + $NoPolice + ";" + $row."Quittance" +";" + $NomAssure + ";" + $NomContractant + ";" + $DateEffet +";" + $DateEmission
          $result = $result + ";"+ $DateEcheance + ";" + $DateEnvoi +";" +$DateReglement +";" +$DateRetour +";"+$DateCompta +";" +$DateComptaAnnul +";" 
          $result = $result + $row."ID Band" +";"+ $row."quittance_nbr_repres" +";" +$TrxPeriod + ";" + $TrxDate +";" + $trxReference + ";" +$trxDescription +";" +$row.Tiers + ";" +$row.code_produit + ";A00;" + $row.Quittance +";"
          return $result
}


function IFCDetailPrefix($row)
{
    $result = ""
    if($row."Code d'actes de Gestion".Substring(0,3) -eq "ENC")
    {
        $result = "EQ"
    }
    if($row."Code d'actes de Gestion".Substring(0,2) -eq "AQ")
    {
        $result = "AQ"
    }

    return $result
}

function IFCDetailEQDC($row)
{
             $result = ""
             
              if($row."DECES MT prime_TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G01;CF01;" + (IFCDetailPrefix $row) +$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3) +"-PRIME_TTC" + ";" + $row."DECES MT prime_TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }



             ### Traitement de : DECES MT prime_HT
             if($row."DECES MT prime_HT" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G01;CF01;"+ (IFCDetailPrefix $row) + $row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3) + "-PRIME_HT" + ";" + $row."DECES MT prime_HT"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }


             ### Traitement de : DECES MT_taxe TSA
             
              if($row."DECES MT_taxe TSA" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G01;CF01;"+ (IFCDetailPrefix $row) +$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-TAXE_TSA" + ";" + $row."DECES MT_taxe TSA"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }


             ### Traitement de : DECES MT_taxe Parafiscale
             
              if($row."DECES MT_taxe Parafiscale" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G01;CF01;"+ (IFCDetailPrefix $row) +$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-TAXE_PARAFISC" + ";" + $row."DECES MT_taxe Parafiscale"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }

             ### Traitement de : DECES MT_chrg_gest
             
              if($row."DECES MT_chrg_gest" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G01;CF01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-CHRG_GST" + ";" + $row."DECES MT_chrg_gest"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }
             
              if($row."DECES MT_chrg_gest" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G01;CF01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-CHRG_GST_CP" + ";" + $row."DECES MT_chrg_gest"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }


              if($row."DECES MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G01;CF01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-COMM_TTC" + ";" + $row."DECES MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }

              if($row."DECES MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G01;CF01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-COMM_TTC_CP" + ";" + $row."DECES MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }
         return $result

}

function IFCDetailEQDTC($row)
{
             $result = ""
             
              if($row."DTC MT prime_TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G07;CF01;" + (IFCDetailPrefix $row) +$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3) +"-PRIME_TTC" + ";" + $row."DTC MT prime_TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }



             ### Traitement de : DTC MT prime_HT
             if($row."DTC MT prime_HT" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G07;CF01;"+ (IFCDetailPrefix $row) + $row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3) + "-PRIME_HT" + ";" + $row."DTC MT prime_HT"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }


             ### Traitement de : DTC MT_taxe TSA
             
              if($row."DTC MT_taxe TSA" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G07;CF01;"+ (IFCDetailPrefix $row) +$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-TAXE_TSA" + ";" + $row."DTC MT_taxe TSA"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }


             ### Traitement de : DTC MT_taxe Parafiscale
             
              if($row."DTC MT_taxe Parafiscale" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G07;CF01;"+ (IFCDetailPrefix $row) +$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-TAXE_PARAFISC" + ";" + $row."DTC MT_taxe Parafiscale"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }

             ### Traitement de : DTC MT_chrg_gest
             
              if($row."DTC MT_chrg_gest" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G07;CF01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-CHRG_GST" + ";" + $row."DTC MT_chrg_gest"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }
             
              if($row."DTC MT_chrg_gest" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G07;CF01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-CHRG_GST_CP" + ";" + $row."DTC MT_chrg_gest"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }


              if($row."DTC MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G07;CF01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-COMM_TTC" + ";" + $row."DTC MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }

              if($row."DTC MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G07;CF01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-COMM_TTC_CP" + ";" + $row."DTC MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }
         return $result

}

function IFCDetailEQIC($row)
{
         $result = ""
          ### Traitement de : IC MT prime_TTC
              if($row."IC MT prime_TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G02;CG01;" + (IFCDetailPrefix $row) + $row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-PRIME_TTC" + ";" + $row."IC MT prime_TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
            
                 }



             ### Traitement de : IC MT prime_HT
             if($row."IC MT prime_HT" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G02;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-PRIME_HT" + ";" + $row."IC MT prime_HT"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }


             ### Traitement de : IC MT_taxe TSA
             
              if($row."IC MT_taxe TSA" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G02;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-TAXE_TSA" + ";" + $row."IC MT_taxe TSA"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }


             ### Traitement de : IC MT_taxe Parafiscale
             
              if($row."IC MT_taxe Parafiscale" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G02;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-TAXE_PARAFISC" + ";" + $row."IC MT_taxe Parafiscale"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }

             ### Traitement de : IC MT_chrg_gest
             
              if($row."IC MT_chrg_gest" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G02;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-CHRG_GST" + ";" + $row."IC MT_chrg_gest"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }

              if($row."IC MT_chrg_gest" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G02;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-CHRG_GST_CP" + ";" + $row."IC MT_chrg_gest"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }


              if($row."IC MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G02;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-COMM_TTC" + ";" + $row."IC MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }
              if($row."IC MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G02;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-COMM_TTC_CP" + ";" + $row."IC MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                 }

        return $result

}

function IFCDetailEQDG($row)
{
        $result=""
                   ### Traitement de : DG MT prime_TTC
              if($row."DG MT prime_TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G03;CG01;" + (IFCDetailPrefix $row) + $row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-PRIME_TTC" + ";" + $row."DG MT prime_TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }



             ### Traitement de : DG MT prime_HT
             if($row."DG MT prime_HT" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G03;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-PRIME_HT" + ";" + $row."DG MT prime_HT"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }


             ### Traitement de : DG MT_taxe TSA
             
              if($row."DG MT_taxe TSA" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G03;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-TAXE_TSA" + ";" + $row."DG MT_taxe TSA"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }


             ### Traitement de : DG MT_taxe Parafiscale
             
              if($row."DG MT_taxe Parafiscale" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G03;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-TAXE_PARAFISC" + ";" + $row."DG MT_taxe Parafiscale"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

             ### Traitement de : DG MT_chrg_gest
             
              if($row."DG MT_chrg_gest" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G03;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-CHRG_GST" + ";" + $row."DG MT_chrg_gest"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }
             if($row."DG MT_chrg_gest" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G03;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-CHRG_GST_CP" + ";" + $row."DG MT_chrg_gest"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }


              if($row."DG MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G03;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-COMM_TTC" + ";" + $row."DG MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }


              if($row."DG MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G03;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-COMM_TTC_CP" + ";" + $row."DG MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }
    return $result

}

function IFCDetailEQBG($row)
{
        $result=""
                       ### Traitement de : BG MT prime_TTC
              if($row."BG MT prime_TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G04;CG01;" + (IFCDetailPrefix $row) + $row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-PRIME_TTC" + ";" + $row."BG MT prime_TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }



             ### Traitement de : BG MT prime_HT
             if($row."BG MT prime_HT" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G04;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-PRIME_HT" + ";" + $row."BG MT prime_HT"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }


             ### Traitement de : BG MT_taxe TSA
             
              if($row."BG MT_taxe TSA" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G04;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-TAXE_TSA" + ";" + $row."BG MT_taxe TSA"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }


             ### Traitement de : BG MT_taxe Parafiscale
             
              if($row."BG MT_taxe Parafiscale" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G04;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-TAXE_PARAFISC" + ";" + $row."BG MT_taxe Parafiscale"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

             ### Traitement de : BG MT_chrg_gest
             
              if($row."BG MT_chrg_gest" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G04;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-CHRG_GST" + ";" + $row."BG MT_chrg_gest"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."BG MT_chrg_gest" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G04;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-CHRG_GST_CP" + ";" + $row."BG MT_chrg_gest"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }


              if($row."BG MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G04;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-COMM_TTC" + ";" + $row."BG MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."BG MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G04;CG01;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-COMM_TTC_CP" + ";" + $row."BG MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }


        return $result
}

function IFCDetailEQEVCAT($row)
{
   $result=""
                 ### Traitement de : EVCAT MT prime_TTC
              if($row."EVCAT MT prime_TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G05;CG02;"+ (IFCDetailPrefix $row) + $row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-PRIME_TTC" + ";" + $row."EVCAT MT prime_TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }



             ### Traitement de : EVCAT MT prime_HT
             if($row."EVCAT MT prime_HT" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G05;CG02;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-PRIME_HT" + ";" + $row."EVCAT MT prime_HT"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }


             ### Traitement de : EVCAT MT_taxe TSA
             
              if($row."EVCAT MT_taxe TSA" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G05;CG02;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3) +"-TAXE_TSA" + ";" + $row."EVCAT MT_taxe TSA"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }


             ### Traitement de : EVCAT MT_taxe Parafiscale
             
              if($row."EVCAT MT_taxe Parafiscale" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G05;CG02;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-TAXE_PARAFISC" + ";" + $row."EVCAT MT_taxe Parafiscale"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

             ### Traitement de : EVCAT MT_chrg_gest
             
              if($row."EVCAT MT_chrg_gest" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G05;CG02;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-CHRG_GST" + ";" + $row."EVCAT MT_chrg_gest"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."EVCAT MT_chrg_gest" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G05;CG02;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-CHRG_GST_CP" + ";" + $row."EVCAT MT_chrg_gest"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }


              if($row."EVCAT MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G05;CG02;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-COMM_TTC" + ";" + $row."EVCAT MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }
  
              if($row."EVCAT MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderEQ $row
                   $newLine = $newLine + "G05;CG02;"+ (IFCDetailPrefix $row)+$row."Code d'actes de Gestion".Substring(3,$row."Code d'actes de Gestion".Length-3)+"-COMM_TTC_CP" + ";" + $row."EVCAT MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }
        return $result
}

function IFCDetailLibComm($row)
{
    $result=""
    ############################################################Liberation de la commission ###################################################

              if($row."DECES MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G01;CF01;"+$row."Code d'actes de Gestion".SubString(0,3) +"-LIB_COMM_TTC" + ";" + $row."DECES MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."DECES MT_COMM" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G01;CF01;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_HT" + ";" + $row."DECES MT_COMM"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }
              if($row."DECES MT_taxe_comm" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G01;CF01;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_TAXE" + ";" + $row."DECES MT_taxe_comm"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

                 if($row."DTC MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G07;CF01;"+$row."Code d'actes de Gestion".SubString(0,3) +"-LIB_COMM_TTC" + ";" + $row."DTC MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."DTC MT_COMM" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G07;CF01;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_HT" + ";" + $row."DTC MT_COMM"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }
              if($row."DTC MT_taxe_comm" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G07;CF01;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_TAXE" + ";" + $row."DTC MT_taxe_comm"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }


              if($row."IC MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G02;CG01;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_TTC" + ";" + $row."IC MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."IC MT_COMM" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G02;CG01;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_HT" + ";" + $row."IC MT_COMM"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."IC MT_taxe_comm" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G02;CG01;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_TAXE" + ";" + $row."IC MT_taxe_comm"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }



              if($row."DG MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G03;CG01;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_TTC" + ";" + $row."DG MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."DG MT_COMM" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G03;CG01;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_HT" + ";" + $row."DG MT_COMM"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."DG MT_taxe_comm" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G03;CG01;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_TAXE" + ";" + $row."DG MT_taxe_comm"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }



              if($row."BG MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G04;CG01;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_TTC" + ";" + $row."BG MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."BG MT_COMM" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G04;CG01;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_HT" + ";" + $row."BG MT_COMM"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."BG MT_taxe_comm" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G04;CG01;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_TAXE" + ";" + $row."BG MT_taxe_comm"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }


              if($row."EVCAT MT_COMM TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G05;CG02;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_TTC" + ";" + $row."EVCAT MT_COMM TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."EVCAT MT_COMM" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G05;CG02;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_HT" + ";" + $row."EVCAT MT_COMM"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."EVCAT MT_taxe_comm" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G05;CG02;"+$row."Code d'actes de Gestion".SubString(0,3)+"-LIB_COMM_TAXE" + ";" + $row."EVCAT MT_taxe_comm"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

    return $result


}

function IFCDetailPAYClient($row)
{
   $result=""
              if($row."DECES MT prime_TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G01;CF01;"+$row."Code d'actes de Gestion"+"-PRIME_TTC_CP" + ";" + $row."DECES MT prime_TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }
                 if($row."DTC MT prime_TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G07;CF01;"+$row."Code d'actes de Gestion"+"-PRIME_TTC_CP" + ";" + $row."DTC MT prime_TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."IC MT prime_TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G02;CG01;"+$row."Code d'actes de Gestion"+"-PRIME_TTC_CP" + ";" + $row."IC MT prime_TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."DG MT prime_TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G03;CG01;"+$row."Code d'actes de Gestion"+"-PRIME_TTC_CP" + ";" + $row."DG MT prime_TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }
              if($row."BG MT prime_TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G04;CG01;"+$row."Code d'actes de Gestion"+"-PRIME_TTC_CP" + ";" + $row."BG MT prime_TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

              if($row."EVCAT MT prime_TTC" -ne $ZERO)
                 {
                   $newLine = IFCHeaderENC $row
                   $newLine = $newLine + "G05;CG02;"+$row."Code d'actes de Gestion"+"-PRIME_TTC_CP" + ";" + $row."EVCAT MT prime_TTC"
                   $result+=$adddNewLine +$newLine 
                   $adddNewLine="`r`n"
                   
                 }

   return $result
}

function IFCDeatilPayBanque($row)
{
    $resultArray =@()
    if($row."MT prime_TTC" -ne $ZERO)
                 {
                        $dateEnc    =  ([Datetime]::ParseExact($row."Date Reglement"   , $dateTimeFormatSource,$null)).ToString('ddMMyyyy')
                        $typeOperation = $row."Code d'actes de Gestion"
                        $MontantEnc = $row."MT prime_TTC"
                        $newItem = [PSCustomObject]@{
                            TypeOperation = $typeOperation
                            DateEncaissement = $dateEnc
                            MtEncaissement = $MontantEnc
                        }

                        $resultArray=$newItem

                 }

    return $resultArray
}

function IFCSummaryPayBanque($array)
{
      $result=""
            $SummarizedBanqueData = ($array | Group-Object -Property @('TypeOperation','DateEncaissement'))
            for ($j=0;$j -le $SummarizedBanqueData.Length-1;$j++)
            {

                $BlockBanque = $SummarizedBanqueData[$j].Group
                $SomeBanque = [math]::Round(($SummarizedBanqueData[$j].Group | Measure-Object -Property 'MtEncaissement' -Sum).Sum,2)
                
                 $CodeIFC = $BlockBanque[0].TypeOperation
                 $TRXDate = $BlockBanque[0].DateEncaissement
                 

                  $TrxPeriod      ="0" + ([Datetime]::ParseExact( $BlockBanque[0].DateEncaissement, 'ddMMyyyy' ,$null)).ToString('MMyyyy')
                  $TrxDate        = ([Datetime]::ParseExact($BlockBanque[0].DateEncaissement, 'ddMMyyyy',$null)).ToString('ddMMyyyy')

                  $trxReference   = $CodeIFC + " " + $TRXDate
                  $trxDescription = $CodeIFC + " " + $TRXDate
                  $Montant        = $SomeBanque

                  $newLine = $CodeIFC + ";;;;;;;;;"+$TrxDate+";;;;;;" + $TrxPeriod + ";" +$TrxDate +";"+ $trxReference+ ";" +$trxDescription +  ";BF001;;;;;CG02;"
                  $newLine = $newLine + $CodeIFC+"TTLBANQUE;"+$Montant
                  $result+=$adddNewLine +$newLine 
                  $adddNewLine="`r`n"
            }

    return $result
}

Try 
{ 
    $items = Get-ChildItem -Path $sourceFolder -ErrorAction Stop | where-object {$_.Attributes -ne "Directory"}
    foreach ($item in $items) 
    {
            $fullItemPath    =$sourceFolder+$item.Name
            $fullItemContent =""
            $adddNewLine     =""
            $lineNumber      =1


            Write-Host "Préparation du fichier : " + $fullItemPath + "  : Phase 1."
            
            $fullTempDestPath=$tempDestinationFolder+($item.Name).Substring(0,($item.Name).LastIndexOf("."))+".TMP"
            $fullDestPath=$destinationFolder+($item.Name).Substring(0,($item.Name).LastIndexOf("."))+".RND"
            $fileContent = (Get-Content $fullItemPath)  
            $fileContent | Set-Content $fullTempDestPath -Force
            (Get-Content $fullTempDestPath)  -replace ("\s+"," ")     | Set-Content $fullTempDestPath -Force 
            (Get-Content $fullTempDestPath)  -replace (" ;",";")      | Set-Content $fullTempDestPath -Force 
            (Get-Content $fullTempDestPath)  -replace ("è","e")       | Set-Content $fullTempDestPath -Force 
            (Get-Content $fullTempDestPath)  -replace ("é","e")       | Set-Content $fullTempDestPath -Force
            (Get-Content $fullTempDestPath)  -replace ("ê","e")       | Set-Content $fullTempDestPath -Force 
            (Get-Content $fullTempDestPath)  -replace (",",";")       | Set-Content $fullTempDestPath -Force 

            (Get-Content $fullTempDestPath)  -replace ("null;",";")   | Set-Content $fullTempDestPath -Force 
            (Get-Content $fullTempDestPath)  -replace ("NULL;",";")   | Set-Content $fullTempDestPath -Force 
            
           
            $newLine = "CodeIFC;NoPolice;NoAdhesion;NomAssure;NomContractant;DateEffet;DateEmission;DateEcheance;DateEnvoi;DateReglement;DateRetour;DateComptaSUNEmission;DateComptaSUNAnnulation;IDBand;QuittanceNombreRepres;DateTrxPeriod;TrxDate;TrxReference;TrxDescription;Agent;Produit;Support;ChampLettrage;Garantie;CompteTakaful;CritereCompte;Montant"

            $fullItemContent+=$adddNewLine +$newLine
            $adddNewLine="`r`n"
            Write-Host "Préparation du fichier : " + $fullItemPath + "  : Phase 2."
            $csvFile     = Import-Csv -Path $fullTempDestPath -Delimiter ";"


            if ($csvFile[0].'Code d''actes de Gestion'.Substring(0,3) -eq "ENC")
                             
            {
               $banqueArray =@()
               foreach($dataRow in $csvFile) 
               {

                    Write-Host "Traitement de l'enregistrement  " $NoEnregistrement " / " ($csvFile.Count)
                    $NoEnregistrement=$NoEnregistrement+1
                    
                    if ($dataRow.'Date Reglement'.Length -gt 0)
                    {

                     
                        $fullItemContent+= IFCDetailEQDC $dataRow
                        $fullItemContent+= IFCDetailEQDTC $dataRow
                        
                        $fullItemContent+= IFCDetailEQIC $dataRow
                        
                        $fullItemContent+= IFCDetailEQDG $dataRow
                        $fullItemContent+= IFCDetailEQBG $dataRow
                        $fullItemContent+= IFCDetailEQEVCAT $dataRow
                        $fullItemContent+= IFCDetailLibComm $dataRow
                        $fullItemContent+= IFCDetailPAYClient $dataRow
                        $banqueArray+=     IFCDeatilPayBanque $dataRow
                        
                    }

               }
               $fullItemContent+= IFCSummaryPayBanque $banqueArray

            }

            
            
            if ($csvFile[0].'Code d''actes de Gestion'.Substring(0,2) -eq "AQ")
            {
                $banqueArray =@()
                foreach($dataRow in $csvFile) 
                {
                    #Write-Host "Traitement de l'enregistrement  " $NoEnregistrement " / " ($csvFile.Count)
                    if ($dataRow.'Code d''actes de Gestion'.Substring(2,1) -eq "P")
                    {
                        Write-Host  "l'enregistrement  " $NoEnregistrement " / " ($csvFile.Count) " sera traité"
                        $fullItemContent+= IFCDetailEQDC $dataRow
                        $fullItemContent+= IFCDetailEQDTC $dataRow
                        $fullItemContent+= IFCDetailEQIC $dataRow                        
                        $fullItemContent+= IFCDetailEQDG $dataRow
                        $fullItemContent+= IFCDetailEQBG $dataRow
                        $fullItemContent+= IFCDetailEQEVCAT $dataRow
                        $fullItemContent+= IFCDetailLibComm $dataRow
                        #Write-Host $fullItemContent
                       # pause
                       # $fullItemContent+= IFCDetailPAYClient $dataRow
                       # $banqueArray+=     IFCDeatilPayBanque $dataRow
                    }
                    else
                    {
                        Write-Host  "l'enregistrement  " $NoEnregistrement " / " ($csvFile.Count) " sera rejeté"
                    }
                    



                   $NoEnregistrement=$NoEnregistrement+1

                }
                $fullItemContent+= IFCSummaryPayBanque $banqueArray
            }
         
            

           [system.io.file]::WriteAllText($fullDestPath, $fullItemContent)
         
          #Move-Item -Path $fullItemPath $originalFolder 

        Remove-Item $fullTempDestPath
     

      }

}
Catch
    {
        Write-Host ((Get-Date).ToString() + " : Une erreur s'est produite lors du traitement. Merci de voir le fichier " + $errorFile)
        Add-Content -Path $errorFile -Value ((Get-Date).ToString() + " : " + $_.Exception.Message)
    }


 ########################  Traitement des écarts ################################


Try 
{ 
    $listOfFiles = Get-ChildItem -Path $destinationFolder -ErrorAction Stop | where-object {$_.Attributes -ne "Directory" -And $_.Extension -eq ".RND"}

    foreach ($pfile in $listOfFiles) 
    {
        $RoundedFile     =$destinationFolder+$pfile.BaseName +".SUN"
        if(Test-Path -Path $RoundedFile)

        {
             Remove-Item $RoundedFile
        }
     
        $tempRoundedFile =$destinationFolder+$pfile.Name
        $MappingData     = Import-Csv -Path $mappingFile  -Delimiter $Separateur
        $CREData         = Import-Csv -Path $tempRoundedFile -Delimiter $Separateur
        $CREData | Add-Member -MemberType NoteProperty "Solde"         -Value [decimal]0
        $CREData | Add-Member -MemberType NoteProperty "Group1" -Value ""
        $CREData | Add-Member -MemberType NoteProperty "Group2" -Value ""
        
       
        for ($i=0; $i -le $CREData.Length-1; $i++) 
        {
        
            $DCFound                   = $MappingData -match $CREData[$i].CritereCompte
            $CREData[$i].Solde         = [math]::Round([decimal]$CREData[$i].Montant,2) *  [math]::Round(([decimal]$DCFound[0].Data),2)
            If($CREData[$i].CritereCompte.SubString(0,2) -eq "EQ")
            {
               $CREData[$i].Group1 = $CREData[$i].Garantie
               $CREData[$i].Group2 = $CREData[$i].NoAdhesion
            }

            If($CREData[$i].CritereCompte -eq "ENCADE-PRIME_TTC_CP" -or $CREData[$i].CritereCompte -eq "ENCADETTLBANQUE")
            {
                $CREData[$i].Group1 = "ENCADE"
                $CREData[$i].group2 = $CREData[$i].TrxDate
            }
            
            If($CREData[$i].CritereCompte -eq "ENCMRB-PRIME_TTC_CP" -or $CREData[$i].CritereCompte -eq "ENCMRBTTLBANQUE")
            {
                $CREData[$i].Group1 = "ENCMRB"
                $CREData[$i].group2 = $CREData[$i].TrxDate
            }
            
            If($CREData[$i].CritereCompte.SubString(0,12) -eq "ENC-LIB_COMM")
            {
                $CREData[$i].Group1 = "ENCLIBCOMM"
                $CREData[$i].group2 = $CREData[$i].TrxDate
            }
            



        }

        
        $SummarizedData = ($CREData | Group-Object -Property @('Group1','Group2'))
        


        for ($j=0;$j -le $SummarizedData.Length-1;$j++)
            {

                $BlockQuittance = $SummarizedData[$j].Group
                      

                $Difference = [math]::Round(($SummarizedData[$j].Group | Measure-Object -Property 'Solde' -Sum).Sum,2)

                Write-Host $BlockQuittance[0].NoAdhesion " : / " $BlockQuittance[0].Group1 " : / " $Difference
                
                if([math]::ABS($Difference) -eq 0 )
                {
                     
                    $BlockQuittance | Export-Csv -Append -Path $RoundedFile -Encoding ASCII -Delimiter ';' -NoTypeInformation
                    
                }
                else
                {

                    $RoundRow = New-Object PsObject -Property @{

                                CodeIFC                =$BlockQuittance[0].CodeIFC
                                NoPolice               =$BlockQuittance[0].NoPolice
                                NoAdhesion             =$BlockQuittance[0].NoAdhesion
                                NomAssure              =$BlockQuittance[0].NomAssure
                                NomContractant         =$BlockQuittance[0].NomContractant
                                DateEffet              =$BlockQuittance[0].DateEffet
                                DateEmission           =$BlockQuittance[0].DateEmission
                                DateEcheance           =$BlockQuittance[0].DateEcheance
                                DateEnvoi              =$BlockQuittance[0].DateEnvoi
                                DateReglement          =$BlockQuittance[0].DateReglement
                                DateRetour             =$BlockQuittance[0].DateRetour
                                DateComptaSUNEmission  =$BlockQuittance[0].DateComptaSUNEmission
                                DateComptaSUNAnnulation=$BlockQuittance[0].DateComptaSUNAnnulation
                                IDBand                 =$BlockQuittance[0].IDBand
                                QuittanceNombreRepres  =$BlockQuittance[0].QuittanceNombreRepres
                                DateTrxPeriod          =$BlockQuittance[0].DateTrxPeriod
                                TrxDate                =$BlockQuittance[0].TrxDate
                                TrxReference           =$BlockQuittance[0].TrxReference
                                TrxDescription         =$BlockQuittance[0].TrxDescription
                                Agent                  =$BlockQuittance[0].Agent
                                Produit                =$BlockQuittance[0].Produit
                                Support                =$BlockQuittance[0].Support
                                ChampLettrage          =$BlockQuittance[0].ChampLettrage
                                Garantie               =$BlockQuittance[0].Garantie
                                CompteTakaful          =$BlockQuittance[0].CompteTakaful
                                CritereCompte          =$BlockQuittance[0].CritereCompte
                                Montant                =([math]::ABS($Difference)).ToString() -replace (",",".");
                                Solde                  = -$Difference;
                                Group1                 = $BlockQuittance[0].Group1;
                                Group2                 = $BlockQuittance[0].Group2}


                    
                     
                   if($Difference -le $SeuilPositif -and $Difference -gt 0.000)
                    {
                       $RoundRow.CritereCompte  = $BlockQuittance[0].CritereCompte.Substring(0,2) +"-" +$CritereAdditionnelSeuilPositif;
                       
                       
                    }
                    if($Difference -ge $SeuilNegatif -and $Difference -lt 0.000)
                    {
                       $RoundRow.CritereCompte  = $BlockQuittance[0].CritereCompte.Substring(0,2) +"-"  +$CritereAdditionnelSeuilNegatif;
                       
                       
                    }

                    if($Difference -lt $SeuilNegatif)
                    {
                       $RoundRow.CritereCompte  = $BlockQuittance[0].CritereCompte.Substring(0,2)  +"-" +$CritereAdditionnelGRANDECARTN;
                       
                    }
                    if($Difference -gt $SeuilPositif)
                    {
                       $RoundRow.CritereCompte  = $BlockQuittance[0].CritereCompte.Substring(0,2)  +"-"  +$CritereAdditionnelGRANDECARTP;
                       
                    }

                        $BlockQuittance | Export-Csv -Append -Path $RoundedFile -Encoding ASCII -Delimiter ';' -NoTypeInformation
                        $RoundRow | Export-Csv -Append -Path $RoundedFile -Encoding ASCII -Delimiter ';' -NoTypeInformation -Force
                        
                    
                    
                }

            }

        (Get-Content $RoundedFile)     -replace ("`"","")     | Set-Content $RoundedFile -Force

        
        Remove-Item ($destinationFolder+$pfile)

        #$SummarizedData.Count
        # $SummarizedData[0].Group
    }

}
Catch
    {
        Write-Host ((Get-Date).ToString() + " : Une erreur s'est produite lors du traitement. Merci de voir le fichier " + $errorFile)
        Add-Content -Path $errorFile -Value ((Get-Date).ToString() + " : " + $_.Exception.Message)
    }
