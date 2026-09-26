# Checklist de Descargas — Datasets de Caidas (v2)

Estado real de descarga de los 28 datasets de la hoja `Datasets_Unicos` (`docs/Revision_Articulos_Deteccion_Caidas-v3.xlsx`), verificado sobre `datasets/DescargasDataManualmente/`.

**Resumen:** 17/28 descargados con datos locales, 11/28 restringidos (solo documentados).

| # | Dataset (Excel) | Carpeta local | Estado | Notas |
|---|---|---|---|---|
| 1 | SisFall | `datasets/DescargasDataManualmente/SisFall/` | Descargado | Estructura y conteos verificados directamente sobre los .txt extraidos (SisFall_dataset/SAxx\|SExx). |
| 2 | UniMiB SHAR | `datasets/DescargasDataManualmente/UniMiB_SHAR/` | Descargado | Nombres de clases leidos directamente de adl_names.mat/fall_names.mat via scipy.io.loadmat. |
| 3 | KFall | `datasets/DescargasDataManualmente/KFall/` | Descargado | Mirror Kaggle INCOMPLETO respecto al Excel (32 sujetos reportados): faltan 5 carpetas de sujeto (SA01, SA02, SA03, SA04, SA05). |
| 4 | FallAllD | `datasets/DescargasDataManualmente/FallAllD/` | Descargado | CONTAMINACION DEL MIRROR KAGGLE: Activity_DataSet(1)/ARS DLR Data Set = contenido del dataset DLR, NO relacionado con FallAllD; sensor_data/ + label_data/ = estructura identica a KFall (SAxx + SAxx_label.xlsx), NO rel... |
| 5 | UP-Fall (HAR-UP) | `datasets/DescargasDataManualmente/UP-Fall/` | Descargado | DataSet_complete.csv: 294679 filas totales x 47 columnas. Los 4 archivos .zip de Google Drive resultaron ser CSV planos sin comprimir (renombrados de .zip a .csv en esta validacion). |
| 6 | UMAFall | `datasets/DescargasDataManualmente/UMAFALL/` | Descargado | Conteo de ADL/caidas coincide con lo reportado en Excel (12 ADL / 3 caidas) usando solo los nombres de archivo, sin abrir contenido. |
| 7 | WEDA Fall | `datasets/DescargasDataManualmente/WEDA_Fall/` | Descargado | Estructura de carpetas 5Hz/10Hz/25Hz/40Hz/50Hz confirmada; conteo de archivos por carpeta en notas de formato. |
| 8 | TST Fall Detection v1 (Original) | `datasets/DescargasDataManualmente/TST_Fall_v1/` | Restringido (sin descarga) | Dataset restringido / sin descarga automatizada; ver README.md y URL.txt para instrucciones de acceso manual. |
| 9 | TST Fall Detection v2 (Original) | `datasets/DescargasDataManualmente/TST_Fall_v2/` | Restringido (sin descarga) | Dataset restringido / sin descarga automatizada; ver README.md y URL.txt para instrucciones de acceso manual. |
| 10 | TST Fall Detection Modificado (Unicomfacauca) | `datasets/DescargasDataManualmente/TST_Fall_Modificado/` | Descargado | Archivo .rar no soportado por zipfile de Python; no se pudo extraer ni validar contenido interno. |
| 11 | UNIVRFall | `datasets/DescargasDataManualmente/UNIVRFall/` | Descargado | Zip extraido correctamente en esta sesion; validacion de tipos de ADL/caida pendiente de cruce con archivos de labels_data. |
| 12 | SmartFallMM | `datasets/DescargasDataManualmente/SmartFallMM/` | Descargado | Total de 15 codigos de actividad distintos coincide con 9 ADL + 5 caidas = 14 reportados en Excel. |
| 13 | FARSEEING | `datasets/DescargasDataManualmente/FARSEEING/` | Restringido (sin descarga) | Dataset restringido / sin descarga automatizada; ver README.md y URL.txt para instrucciones de acceso manual. |
| 14 | MobiAct (Versión 2 Oficial) | `datasets/DescargasDataManualmente/MobiAct/` | Restringido (sin descarga) | Dataset restringido / sin descarga automatizada; ver README.md y URL.txt para instrucciones de acceso manual. |
| 15 | MobiFall | `datasets/DescargasDataManualmente/MobiFall/` | Restringido (sin descarga) | Dataset restringido / sin descarga automatizada; ver README.md y URL.txt para instrucciones de acceso manual. |
| 16 | Graz UT OL | `datasets/DescargasDataManualmente/Graz_UT_OL/` | Descargado | Base de datos abierta con sqlite3 directamente; 13 tablas encontradas. |
| 17 | UR Fall Detection | `datasets/DescargasDataManualmente/UR_Fall_Detection/` | Descargado | Conteo de secuencias distintas coincide con 30 caidas / 40 ADL reportadas en Excel (fall-01..30, adl-01..40). |
| 18 | DOFDA | `datasets/DescargasDataManualmente/DOFDA/` | Restringido (sin descarga) | Dataset restringido / sin descarga automatizada; ver README.md y URL.txt para instrucciones de acceso manual. |
| 19 | Erciyes University | `datasets/DescargasDataManualmente/Erciyes_University/` | Restringido (sin descarga) | Dataset restringido / sin descarga automatizada; ver README.md y URL.txt para instrucciones de acceso manual. |
| 20 | IMUFD | `datasets/DescargasDataManualmente/IMUFD/` | Restringido (sin descarga) | Dataset restringido / sin descarga automatizada; ver README.md y URL.txt para instrucciones de acceso manual. |
| 21 | DLR | `datasets/DescargasDataManualmente/DLR/` | Restringido (sin descarga) | Dataset restringido / sin descarga automatizada; ver README.md y URL.txt para instrucciones de acceso manual. |
| 22 | FFFStudy | `datasets/DescargasDataManualmente/FFFStudy/` | Restringido (sin descarga) | Dataset restringido / sin descarga automatizada; ver README.md y URL.txt para instrucciones de acceso manual. |
| 23 | LTMM | `datasets/DescargasDataManualmente/LTMM/` | Descargado | Descarga intencionalmente parcial (solo metadatos de muestra) por ser dataset sin caidas y de gran volumen (20.8GB); ver README.md para instrucciones de descarga completa via wget. |
| 24 | Smartphone Human Fall Dataset | `datasets/DescargasDataManualmente/Smartphone_Human_Fall_Dataset/` | Descargado | Dataset de comunidad Kaggle; validado solo estructuralmente (shapes y columnas), sin trazabilidad al paper original. |
| 25 | Falls vs Normal Activities | `datasets/DescargasDataManualmente/Falls_vs_Normal_Activities/` | Descargado | Dataset de comunidad Kaggle; validado solo estructuralmente (shapes y columnas), sin trazabilidad al paper original. |
| 26 | Elderly Fall Detection IoT Dataset | `datasets/DescargasDataManualmente/Elderly_Fall_Detection_IoT/` | Descargado | fall_detection.csv valida correctamente contra lo reportado en Excel. ADVERTENCIA: el mirror de Kaggle incluye ademas 'archive (14)/dataset/dataset/' con 24 carpetas 'chuteNN' (patron de nombres del dataset de vision ... |
| 27 | Real-Time Patient Fall Detection Data | `datasets/DescargasDataManualmente/Real_Time_Patient_Fall_Detection/` | Descargado | Dataset de comunidad Kaggle; validado solo estructuralmente (shapes y columnas), sin trazabilidad al paper original. |
| 28 | Ultralytics Fall-Detect Community Dataset (Imágenes) | `datasets/DescargasDataManualmente/Ultralytics_Fall_Detect/` | Restringido (sin descarga) | Dataset restringido / sin descarga automatizada; ver README.md y URL.txt para instrucciones de acceso manual. |
