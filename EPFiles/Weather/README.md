# Weather files

TMYx 2011–2025 files (typical meteorological years from the 2011–2025 period)
from https://climate.onebuilding.org, picked to cover a wide range of climates.

| File | Climate (Köppen) | Tmean °C | Tmin / Tmax °C | GHI kWh/m²a | HDD18 | CDD18 |
|---|---|---|---|---|---|---|
| DEU_SH_Kiel.Holtenau.AP | Cfb, maritime N-Germany | 9.8 | -9.0 / 30.0 | 1081 | 3113 | 112 |
| DEU_BE_Berlin-Dahlem* | Cfb/Dfb, continental-ish | 10.8 | -9.2 / 36.9 | 1122 | 2940 | 301 |
| DEU_BW_Stuttgart.AP | Cfb, S-Germany | 10.9 | -6.0 / 32.0 | 1220 | 2897 | 316 |
| DEU_BW_Freiburg.AP* | Cfb, warmest DE region | 10.6 | -10.0 / 33.6 | 1270 | 2987 | 269 |
| DEU_BY_Oberstdorf* | Dfb, alpine 807 m | 5.5 | -20.1 / 28.2 | 1277 | 4612 | 60 |
| GRC_AT_Athinai-Hellinikon | Csa, Mediterranean | 19.1 | 0.9 / 39.6 | 1771 | 937 | 1334 |
| AUS_NSW_Sydney.Obs | Cfa, humid subtropical, S hemisphere | 18.4 | 6.2 / 36.0 | 1747 | 638 | 798 |
| USA_CO_Denver.Intl.AP | BSk, semi-arid, 1650 m | 11.4 | -21.1 / 37.2 | 1877 | 3129 | 707 |
| USA_AK_Fairbanks.Intl.AP | Dsc/Dfc, subarctic | -0.9 | -42.0 / 28.9 | 980 | 7036 | 133 |
| IND_DL_New.Delhi-Safdarjung.AP | Cwa, monsoon | 25.1 | 5.0 / 45.6 | 1898 | 415 | 3007 |
| ARE_DU_Dubai.Intl.AP | BWh, hot desert | 29.7 | 12.4 / 47.0 | 2192 | 19 | 4306 |
| SGP_SG_Singapore-Changi.Intl.AP | Af, tropical rainforest | 28.0 | 22.9 / 34.0 | 1769 | 0 | 3639 |

\* Built from ERA5 reanalysis rather than station measurements (source field `ERA5-TMYx` in the header).

The statistics were computed from the hourly dry-bulb temperature and global horizontal irradiance.
Degree-days use an 18 °C base.
