# Weather files

TMYx 2011–2025 files (typical meteorological years from the 2011–2025 period)
from https://climate.onebuilding.org, picked to cover a wide range of climates.

| File | Climate (Köppen) | Tmean °C | Tmin / Tmax °C | GHI kWh/m²a | HDD18 (heating) | CDD18 (cooling) | Precip mm/a | RH mean % | Snow-cover h |
|---|---|---|---|---|---|---|---|---|---|
| DEU_SH_Kiel.Holtenau.AP | Cfb, maritime N-Germany | 9.8 | -9.0 / 30.0 | 1081 | 3113 | 112 | 802 | 79 | 499 |
| DEU_BE_Berlin-Dahlem* | Cfb/Dfb, continental-ish | 10.8 | -9.2 / 36.9 | 1122 | 2940 | 301 | 646 | 75 | 195 |
| DEU_BW_Stuttgart.AP | Cfb, S-Germany | 10.9 | -6.0 / 32.0 | 1220 | 2897 | 316 | 833 | 74 | 1026 |
| DEU_BW_Freiburg.AP* | Cfb, warmest DE region | 10.6 | -10.0 / 33.6 | 1270 | 2987 | 269 | 1095 | 77 | 865 |
| DEU_BY_Oberstdorf* | Dfb, alpine 807 m | 5.5 | -20.1 / 28.2 | 1277 | 4612 | 60 | 1851 | 79 | 5130 |
| GRC_AT_Athinai-Hellinikon | Csa, Mediterranean | 19.1 | 0.9 / 39.6 | 1771 | 937 | 1334 | 384 | 62 | 5 |
| AUS_NSW_Sydney.Obs | Cfa, humid subtropical, S hemisphere | 18.4 | 6.2 / 36.0 | 1747 | 638 | 798 | 921 | 67 | 0 |
| USA_CO_Denver.Intl.AP | BSk, semi-arid, 1650 m | 11.4 | -21.1 / 37.2 | 1877 | 3129 | 707 | 392 | 50 | 1894 |
| USA_AK_Fairbanks.Intl.AP | Dsc/Dfc, subarctic | -0.9 | -42.0 / 28.9 | 980 | 7036 | 133 | 381 | 68 | 4254 |
| IND_DL_New.Delhi-Safdarjung.AP | Cwa, monsoon | 25.1 | 5.0 / 45.6 | 1898 | 415 | 3007 | 755 | 67 | 0 |
| ARE_DU_Dubai.Intl.AP | BWh, hot desert | 29.7 | 12.4 / 47.0 | 2192 | 19 | 4306 | 50 | 54 | 0 |
| SGP_SG_Singapore-Changi.Intl.AP | Af, tropical rainforest | 28.0 | 22.9 / 34.0 | 1769 | 0 | 3639 | 2602 | 80 | 0 |

\* Built from ERA5 reanalysis rather than station measurements (source field `ERA5-TMYx` in the header).

The statistics were computed from the hourly dry-bulb temperature and global horizontal irradiance.

**Column meanings**

- **Tmean / Tmin / Tmax**: annual mean, lowest and highest hourly outdoor air temperature.
- **GHI**: annual global horizontal irradiance, i.e. total solar energy falling on a horizontal surface.
- **HDD18 (heating degree days, base 18 °C)**: indicates how much heating a location needs.
  For each day, the amount by which the outdoor temperature is below 18 °C is summed over the year.
  Example: one day at 8 °C contributes 10 K·d. Higher value = colder climate, more heating demand.
- **CDD18 (cooling degree days, base 18 °C)**: the same in the other direction. The amount by which
  the outdoor temperature is above 18 °C is summed over the year. Higher value = more cooling demand.

- **Precip**: annual liquid precipitation (rain, plus snow as water equivalent) in mm.
- **RH mean**: annual mean relative humidity of the outdoor air.
- **Snow-cover h**: number of hours with snow on the ground.

Note: a TMYx year is stitched together from typical months of different years. Its precipitation
total can therefore differ noticeably from the long-term mean and should only be used as a rough indicator.

Degree days here are calculated from hourly values (sum of hourly differences / 24), unit K·d.
