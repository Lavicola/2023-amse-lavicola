# Project Plan

## Summary
Analysis of the charger infrastructure and the registration of BEV in Germany from 2009 - 2022
## Rationale
Germany recognized e-mobility as core technology for itself and the industry at an early stage. In 2009, the National Electromobility Development Plan of the Federal Government was adopted, which was to ensure in 3 phases that Germany takes a leading role in electromobility. The analysis shows the goal for the three defined phases in the area of infrastructure and vehicles and then shows the reality for these years.
In addition the analysis also shows the results after 2020.
## Datasources

### Datasource1: Liste der Ladesäulen
* Metadata URL: /
* Data URL: https://www.bundesnetzagentur.de/SharedDocs/Downloads/DE/Sachgebiete/Energie/Unternehmen_Institutionen/E_Mobilitaet/Ladesaeulenregister_CSV.csv?__blob=publicationFile&v=46
* Data Type: CSV
* Licence: Lizenz CC BY 4.0 (bundesnetzagentur.de)
This data source shows the exact coordinates of the charging stations, contains the charging points as well as their amperage and also indicates the commissioning of the station.


### Datasource2: Neuzulassung von Kraftfahrzeugen
* Metadata URL: /
* Data URL: [https://www.kba.de/DE/Statistik/Produktkatalog/produkte/Fahrzeuge/fz8/fz8_gentab.html;jsessionid=FAB7EB31182B3E967B07899A2BE2623E.live21322?nn=3547466](https://www.kba.de/DE/Statistik/Fahrzeuge/Neuzulassungen/Umwelt/n_umwelt_node.html;?yearFilter=2022)
* Data Type: HTML / xlsxx (depending on the year)
* Licence: Datenlizenz Deutschland – Namensnennung – Version 2.0 (Kraftfahrt-Bundesamt, Flensburg)
This data source shows the monthly registration of electric cars. Since the data is published mixed either via HTML or XLSX, a small scraper has to be built here to analyze the page and merge the needed data.


### Datasource3: Neuzulassungen von Personenkraftwagen (PKW) nach Segmenten und Modellreihen im Jahr 2023 (FZ 11)
<del>
* Metadata URL: https://mobilithek.info/offers/573358146154541056
* Data URL: https://www.kba.de/SharedDocs/Downloads/DE/Statistik/Fahrzeuge/FZ11/fz11_2023_01.xlsx?__blob=publicationFile&v=5
* Data Type: HTML
The data source shows new passenger vehicle registrations by segment and model series for January 2023. These data sources also exist for other years and months.
[See the full list here](https://mobilithek.info/offers?searchString=%22Neuzulassungen%20von%20Personenkraftwagen%22&page=2)
</del><br>
--> Data was checked, but does not contain drive information

## Work Packages
1. Analyze the Data of the different Datasources and their uses in this Project.
2. Analyze the Structure of second Datasource and build a Script to download and store the different statistics into a Database 
3. TBA
## Technology Stack
### Data engineering
In order to get information of the second Datasource it is necessary to build a small tool which is able to extract these Information.
For that the programming language Python will be used in combination with libraries like requests to get the website and beautifulsoup to analyze the Website and the Data.
Furthermore sqlite will be used to store the extracted Information in a database. To read CSV Files pandas will be used.
### Data exploration
Jupyter Notebook in combination with DB Browser
### Data analysis
Jupyter Notebook
### Data Pipeline
![Dataflow in the Pipeline](data_pipeline.drawio.svg)


