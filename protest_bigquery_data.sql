SELECT
  GLOBALEVENTID,
  SQLDATE,
  MonthYear,
  Year,
  Actor1Name,
  Actor1Code,
  Actor1CountryCode,
  Actor2Name,
  Actor2Code,
  Actor2CountryCode,
  EventCode,
  EventRootCode,
  IsRootEvent,
  ActionGeo_FullName,
  ActionGeo_CountryCode,
  ActionGeo_ADM1Code,
  ActionGeo_Lat,
  ActionGeo_Long,
  GoldsteinScale,
  NumMentions,
  NumSources,
  NumArticles,
  AvgTone,
  SOURCEURL,
  CASE
    WHEN EventCode LIKE '141%' THEN 'Demonstration/Rally'
    WHEN EventCode LIKE '142%' THEN 'Hunger Strike'
    WHEN EventCode LIKE '143%' THEN 'Strike/Boycott'
    WHEN EventCode LIKE '144%' THEN 'Obstruction/Blockade'
    WHEN EventCode LIKE '145%' THEN 'Violent Protest/Riot'
    WHEN EventCode = '140' THEN 'Other Political Dissent'
    ELSE 'Uncategorized Protest'
  END AS ProtestCategory,
  CASE
     WHEN EventCode LIKE '14_1' THEN 'Leadership Change'
     WHEN EventCode LIKE '14_2' THEN 'Policy Change'
     WHEN EventCode LIKE '14_3' THEN 'Rights'
     WHEN EventCode LIKE '14_4' THEN 'Regime/Institution Change'
     ELSE 'Reason Not Specified'
  END AS ProtestReason
FROM `gdelt-bq.gdeltv2.events` 
WHERE 
  IsRootEvent = 1 --double check unique lat/lon count without filtering as root
  AND EventRootCode = '14'
  AND ActionGeo_CountryCode = 'US'
  AND Year IN (2020, 2021, 2022, 2023, 2024, 2025)
  AND NumArticles > 1
  AND AvgTone < -5