import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv
import requests.exceptions

# 1. SETUP: Load the API key securely from the .env file
load_dotenv()
API_KEY = os.getenv("SPORTRADAR_API_KEY")

# Sportradar API URL structure
ACCESS_LEVEL = "trial"
VERSION = "v4"  
LANGUAGE = "en"
BASE_URL = f"https://api.sportradar.com/soccer/{ACCESS_LEVEL}/{VERSION}/{LANGUAGE}"

# 2. THE MATCH IDS: Paste the IDs you found from the website here!
MATCH_IDS = [
        "sr:sport_event:28710580",  # 2021-09-01 | Central African Republic vs Cape Verde
        "sr:sport_event:28712626",  # 2021-09-01 | Senegal vs Togo
        "sr:sport_event:24832798",  # 2021-09-01 | Portugal vs Ireland
        "sr:sport_event:24833896",  # 2021-09-01 | France vs Bosnia and Herzegovina
        "sr:sport_event:24834162",  # 2021-09-01 | Denmark vs Scotland
        "sr:sport_event:24834166",  # 2021-09-01 | Moldova vs Austria
        "sr:sport_event:24834790",  # 2021-09-01 | Norway vs Netherlands
        "sr:sport_event:24835206",  # 2021-09-01 | Russia vs Croatia
        "sr:sport_event:28712022",  # 2021-09-01 | Egypt vs Angola
        "sr:sport_event:20718043",  # 2021-09-02 | Ecuador vs Paraguay
        "sr:sport_event:20718039",  # 2021-09-02 | Bolivia vs Colombia
        "sr:sport_event:28712930",  # 2021-09-02 | Morocco vs Sudan
        "sr:sport_event:28709944",  # 2021-09-02 | Algeria vs Djibouti
        "sr:sport_event:24835680",  # 2021-09-02 | Liechtenstein vs Germany
        "sr:sport_event:24835448",  # 2021-09-02 | Hungary vs England
        "sr:sport_event:24834032",  # 2021-09-02 | Estonia vs Belgium
        "sr:sport_event:27976796",  # 2021-09-02 | Saudi Arabia vs Vietnam
        "sr:sport_event:27976794",  # 2021-09-02 | Australia vs China PR
        "sr:sport_event:27976562",  # 2021-09-02 | Korea Republic vs Iraq
        "sr:sport_event:27976792",  # 2021-09-02 | Japan vs Oman
        "sr:sport_event:24833428",  # 2021-09-02 | Sweden vs Spain
        "sr:sport_event:28712230",  # 2021-09-03 | Ghana vs Ethiopia
        "sr:sport_event:28710360",  # 2021-09-03 | Tunisia vs Equatorial Guinea
        "sr:sport_event:27747484",  # 2021-09-03 | Canada vs Honduras
        "sr:sport_event:28711872",  # 2021-09-03 | Mozambique vs Ivory Coast
        "sr:sport_event:27747482",  # 2021-09-03 | Mexico vs Jamaica
        "sr:sport_event:27747480",  # 2021-09-03 | Panama vs Costa Rica
        "sr:sport_event:20718041",  # 2021-09-03 | Chile vs Brazil
        "sr:sport_event:20718037",  # 2021-09-03 | Peru vs Uruguay
        "sr:sport_event:20718035",  # 2021-09-03 | Venezuela vs Argentina
        "sr:sport_event:28712232",  # 2021-09-03 | Zimbabwe vs South Africa
        "sr:sport_event:24835216",  # 2021-09-04 | Slovakia vs Croatia
        "sr:sport_event:24834798",  # 2021-09-04 | Netherlands vs Montenegro
        "sr:sport_event:24834244",  # 2021-09-04 | Scotland vs Moldova
        "sr:sport_event:24834242",  # 2021-09-04 | Israel vs Austria
        "sr:sport_event:24834800",  # 2021-09-04 | Latvia vs Norway
        "sr:sport_event:24833904",  # 2021-09-04 | Ukraine vs France
        "sr:sport_event:28681538",  # 2021-09-05 | Ecuador vs Chile
        "sr:sport_event:27747490",  # 2021-09-05 | Costa Rica vs Mexico
        "sr:sport_event:28681542",  # 2021-09-05 | Uruguay vs Bolivia
        "sr:sport_event:28681540",  # 2021-09-05 | Paraguay vs Colombia
        "sr:sport_event:27747492",  # 2021-09-05 | Jamaica vs Panama
        "sr:sport_event:28712026",  # 2021-09-05 | Gabon vs Egypt
        "sr:sport_event:24835690",  # 2021-09-05 | Germany vs Armenia
        "sr:sport_event:28681536",  # 2021-09-05 | Brazil vs Argentina
        "sr:sport_event:24834034",  # 2021-09-05 | Belgium vs Czechia
        "sr:sport_event:24833628",  # 2021-09-05 | Switzerland vs Italy
        "sr:sport_event:24833502",  # 2021-09-05 | Spain vs Georgia
        "sr:sport_event:24835454",  # 2021-09-05 | England vs Andorra
        "sr:sport_event:27747486",  # 2021-09-06 | USA vs Canada
        "sr:sport_event:28712246",  # 2021-09-06 | South Africa vs Ghana
        "sr:sport_event:28712934",  # 2021-09-06 | Guinea vs Morocco
        "sr:sport_event:28711876",  # 2021-09-06 | Ivory Coast vs Cameroon
        "sr:sport_event:27976622",  # 2021-09-07 | Iraq vs IR Iran
        "sr:sport_event:24833906",  # 2021-09-07 | Bosnia and Herzegovina vs Kazakhstan
        "sr:sport_event:28712814",  # 2021-09-07 | Congo Republic vs Senegal
        "sr:sport_event:24834246",  # 2021-09-07 | Austria vs Scotland
        "sr:sport_event:24834812",  # 2021-09-07 | Netherlands vs Turkiye
        "sr:sport_event:24834814",  # 2021-09-07 | Norway vs Gibraltar
        "sr:sport_event:24835230",  # 2021-09-07 | Croatia vs Slovenia
        "sr:sport_event:24833910",  # 2021-09-07 | France vs Finland
        "sr:sport_event:28710054",  # 2021-09-07 | Burkina Faso vs Algeria
        "sr:sport_event:27976798",  # 2021-09-07 | Oman vs Saudi Arabia
        "sr:sport_event:28710366",  # 2021-09-07 | Zambia vs Tunisia
        "sr:sport_event:24832892",  # 2021-09-07 | Azerbaijan vs Portugal
        "sr:sport_event:27976802",  # 2021-09-07 | China PR vs Japan
        "sr:sport_event:28710650",  # 2021-09-07 | Cape Verde vs Nigeria
        "sr:sport_event:27976800",  # 2021-09-07 | Vietnam vs Australia
        "sr:sport_event:24835708",  # 2021-09-08 | Iceland vs Germany
        "sr:sport_event:24835470",  # 2021-09-08 | Poland vs England
        "sr:sport_event:24834038",  # 2021-09-08 | Belarus vs Belgium
        "sr:sport_event:27747494",  # 2021-09-08 | Canada vs El Salvador
        "sr:sport_event:24833510",  # 2021-09-08 | Kosovo vs Spain
        "sr:sport_event:24833508",  # 2021-09-08 | Greece vs Sweden
        "sr:sport_event:24833702",  # 2021-09-08 | Northern Ireland vs Switzerland
        "sr:sport_event:20718055",  # 2021-10-07 | Paraguay vs Argentina
        "sr:sport_event:28710370",  # 2021-10-07 | Tunisia vs Mauritania
        "sr:sport_event:20718061",  # 2021-10-07 | Venezuela vs Brazil
        "sr:sport_event:20718057",  # 2021-10-07 | Uruguay vs Colombia
        "sr:sport_event:27977128",  # 2021-10-07 | Australia vs Oman
        "sr:sport_event:27977122",  # 2021-10-07 | Saudi Arabia vs Japan
        "sr:sport_event:27976636",  # 2021-10-07 | Iraq vs Lebanon
        "sr:sport_event:28711046",  # 2021-10-07 | Liberia vs Cape Verde
        "sr:sport_event:28712032",  # 2021-10-08 | Egypt vs Libya
        "sr:sport_event:28710088",  # 2021-10-08 | Algeria vs Niger
        "sr:sport_event:24835718",  # 2021-10-08 | Germany vs Romania
        "sr:sport_event:24835238",  # 2021-10-08 | Cyprus vs Croatia
        "sr:sport_event:24834820",  # 2021-10-08 | Turkiye vs Norway
        "sr:sport_event:24834818",  # 2021-10-08 | Latvia vs Netherlands
        "sr:sport_event:28711884",  # 2021-10-08 | Malawi vs Ivory Coast
        "sr:sport_event:27747504",  # 2021-10-08 | El Salvador vs Panama
        "sr:sport_event:27747508",  # 2021-10-08 | Mexico vs Canada
        "sr:sport_event:20718063",  # 2021-10-08 | Ecuador vs Bolivia
        "sr:sport_event:24834252",  # 2021-10-09 | Faroe Islands vs Austria
        "sr:sport_event:28713468",  # 2021-10-09 | Guinea-Bissau vs Morocco
        "sr:sport_event:28712818",  # 2021-10-09 | Senegal vs Namibia
        "sr:sport_event:24833714",  # 2021-10-09 | Switzerland vs Northern Ireland
        "sr:sport_event:24835488",  # 2021-10-09 | Andorra vs England
        "sr:sport_event:24834254",  # 2021-10-09 | Scotland vs Israel
        "sr:sport_event:24833916",  # 2021-10-09 | Kazakhstan vs Bosnia and Herzegovina
        "sr:sport_event:28712342",  # 2021-10-09 | Ethiopia vs South Africa
        "sr:sport_event:28712340",  # 2021-10-09 | Ghana vs Zimbabwe
        "sr:sport_event:24833516",  # 2021-10-09 | Sweden vs Kosovo
        "sr:sport_event:28711118",  # 2021-10-10 | Cape Verde vs Liberia
        "sr:sport_event:28710468",  # 2021-10-10 | Mauritania vs Tunisia
        "sr:sport_event:29305284",  # 2021-10-10 | Venezuela vs Ecuador
        "sr:sport_event:27747510",  # 2021-10-10 | Jamaica vs Canada
        "sr:sport_event:27747516",  # 2021-10-10 | Panama vs USA
        "sr:sport_event:27747512",  # 2021-10-10 | Mexico vs Honduras
        "sr:sport_event:29305294",  # 2021-10-10 | Argentina vs Uruguay
        "sr:sport_event:29305292",  # 2021-10-10 | Colombia vs Brazil
        "sr:sport_event:24834826",  # 2021-10-11 | Norway vs Montenegro
        "sr:sport_event:24835730",  # 2021-10-11 | North Macedonia vs Germany
        "sr:sport_event:24835246",  # 2021-10-11 | Croatia vs Slovakia
        "sr:sport_event:28712036",  # 2021-10-11 | Libya vs Egypt
        "sr:sport_event:24834824",  # 2021-10-11 | Netherlands vs Gibraltar
        "sr:sport_event:28711888",  # 2021-10-11 | Ivory Coast vs Malawi
        "sr:sport_event:29305298",  # 2021-10-11 | Chile vs Paraguay
        "sr:sport_event:27977136",  # 2021-10-12 | Saudi Arabia vs China PR
        "sr:sport_event:24835496",  # 2021-10-12 | England vs Hungary
        "sr:sport_event:24834270",  # 2021-10-12 | Faroe Islands vs Scotland
        "sr:sport_event:29458418",  # 2021-10-12 | Guinea vs Morocco
        "sr:sport_event:24834268",  # 2021-10-12 | Denmark vs Austria
        "sr:sport_event:24833958",  # 2021-10-12 | Ukraine vs Bosnia and Herzegovina
        "sr:sport_event:24833858",  # 2021-10-12 | Lithuania vs Switzerland
        "sr:sport_event:24833520",  # 2021-10-12 | Sweden vs Greece
        "sr:sport_event:24832946",  # 2021-10-12 | Portugal vs Luxembourg
        "sr:sport_event:27976644",  # 2021-10-12 | United Arab Emirates vs Iraq
        "sr:sport_event:27977138",  # 2021-10-12 | Japan vs Australia
        "sr:sport_event:28712344",  # 2021-10-12 | Zimbabwe vs Ghana
        "sr:sport_event:28712914",  # 2021-10-12 | Namibia vs Senegal
        "sr:sport_event:28710166",  # 2021-10-12 | Niger vs Algeria
        "sr:sport_event:28712346",  # 2021-10-12 | South Africa vs Ethiopia
        "sr:sport_event:27747518",  # 2021-10-13 | Canada vs Panama
        "sr:sport_event:27747522",  # 2021-10-14 | El Salvador vs Mexico
        "sr:sport_event:20718067",  # 2021-10-14 | Bolivia vs Paraguay
        "sr:sport_event:20718071",  # 2021-10-14 | Colombia vs Ecuador
        "sr:sport_event:20718073",  # 2021-10-14 | Argentina vs Peru
        "sr:sport_event:24835258",  # 2021-11-11 | Malta vs Croatia
        "sr:sport_event:24833590",  # 2021-11-11 | Greece vs Spain
        "sr:sport_event:20718081",  # 2021-11-11 | Paraguay vs Chile
        "sr:sport_event:20718083",  # 2021-11-11 | Ecuador vs Venezuela
        "sr:sport_event:24833110",  # 2021-11-11 | Ireland vs Portugal
        "sr:sport_event:24835736",  # 2021-11-11 | Germany vs Liechtenstein
        "sr:sport_event:28712918",  # 2021-11-11 | Togo vs Senegal
        "sr:sport_event:24833588",  # 2021-11-11 | Georgia vs Sweden
        "sr:sport_event:27976650",  # 2021-11-11 | Iraq vs Syria
        "sr:sport_event:28712350",  # 2021-11-11 | Ethiopia vs Ghana
        "sr:sport_event:27977152",  # 2021-11-11 | Vietnam vs Japan
        "sr:sport_event:27977156",  # 2021-11-11 | Australia vs Saudi Arabia
        "sr:sport_event:28712352",  # 2021-11-11 | South Africa vs Zimbabwe
        "sr:sport_event:28712040",  # 2021-11-12 | Angola vs Egypt
        "sr:sport_event:20718075",  # 2021-11-12 | Uruguay vs Argentina
        "sr:sport_event:24835514",  # 2021-11-12 | England vs Albania
        "sr:sport_event:24834274",  # 2021-11-12 | Austria vs Israel
        "sr:sport_event:24833864",  # 2021-11-12 | Italy vs Switzerland
        "sr:sport_event:28714774",  # 2021-11-12 | Sudan vs Morocco
        "sr:sport_event:24834350",  # 2021-11-12 | Moldova vs Scotland
        "sr:sport_event:28710260",  # 2021-11-12 | Djibouti vs Algeria
        "sr:sport_event:20718079",  # 2021-11-12 | Brazil vs Colombia
        "sr:sport_event:24834840",  # 2021-11-13 | Montenegro vs Netherlands
        "sr:sport_event:24834122",  # 2021-11-13 | Belgium vs Estonia
        "sr:sport_event:24833966",  # 2021-11-13 | France vs Kazakhstan
        "sr:sport_event:28711892",  # 2021-11-13 | Ivory Coast vs Mozambique
        "sr:sport_event:24834832",  # 2021-11-13 | Norway vs Latvia
        "sr:sport_event:27747532",  # 2021-11-13 | USA vs Mexico
        "sr:sport_event:28710472",  # 2021-11-13 | Equatorial Guinea vs Tunisia
        "sr:sport_event:24833964",  # 2021-11-13 | Bosnia and Herzegovina vs Finland
        "sr:sport_event:27747526",  # 2021-11-13 | Canada vs Costa Rica
        "sr:sport_event:27747528",  # 2021-11-13 | Honduras vs Panama
        "sr:sport_event:28711122",  # 2021-11-13 | Cape Verde vs Central African Republic
        "sr:sport_event:24833114",  # 2021-11-14 | Portugal vs Serbia
        "sr:sport_event:24833594",  # 2021-11-14 | Spain vs Sweden
        "sr:sport_event:28712924",  # 2021-11-14 | Senegal vs Congo Republic
        "sr:sport_event:24835748",  # 2021-11-14 | Armenia vs Germany
        "sr:sport_event:24835264",  # 2021-11-14 | Croatia vs Russia
        "sr:sport_event:28712354",  # 2021-11-14 | Ghana vs South Africa
        "sr:sport_event:24833872",  # 2021-11-15 | Switzerland vs Bulgaria
        "sr:sport_event:24834352",  # 2021-11-15 | Austria vs Moldova
        "sr:sport_event:24834356",  # 2021-11-15 | Scotland vs Denmark
        "sr:sport_event:24835528",  # 2021-11-15 | San Marino vs England
        "sr:sport_event:28710476",  # 2021-11-16 | Tunisia vs Zambia
        "sr:sport_event:28711894",  # 2021-11-16 | Cameroon vs Ivory Coast
        "sr:sport_event:24833968",  # 2021-11-16 | Bosnia and Herzegovina vs Ukraine
        "sr:sport_event:24833970",  # 2021-11-16 | Finland vs France
        "sr:sport_event:24834848",  # 2021-11-16 | Netherlands vs Norway
        "sr:sport_event:20718087",  # 2021-11-16 | Bolivia vs Uruguay
        "sr:sport_event:20718091",  # 2021-11-16 | Colombia vs Paraguay
        "sr:sport_event:20718093",  # 2021-11-16 | Argentina vs Brazil
        "sr:sport_event:24834126",  # 2021-11-16 | Wales vs Belgium
        "sr:sport_event:28714778",  # 2021-11-16 | Morocco vs Guinea
        "sr:sport_event:28712044",  # 2021-11-16 | Egypt vs Gabon
        "sr:sport_event:27976660",  # 2021-11-16 | Iraq vs Korea Republic
        "sr:sport_event:27977190",  # 2021-11-16 | China PR vs Australia
        "sr:sport_event:27977192",  # 2021-11-16 | Vietnam vs Saudi Arabia
        "sr:sport_event:27977188",  # 2021-11-16 | Oman vs Japan
        "sr:sport_event:28711208",  # 2021-11-16 | Nigeria vs Cape Verde
        "sr:sport_event:28710266",  # 2021-11-16 | Algeria vs Burkina Faso
        "sr:sport_event:20718085",  # 2021-11-17 | Chile vs Ecuador
        "sr:sport_event:27747540",  # 2021-11-17 | Panama vs El Salvador
        "sr:sport_event:27747534",  # 2021-11-17 | Canada vs Mexico
        "sr:sport_event:27977204",  # 2022-01-27 | Australia vs Vietnam
        "sr:sport_event:27977206",  # 2022-01-27 | Japan vs China PR
        "sr:sport_event:27976668",  # 2022-01-27 | IR Iran vs Iraq
        "sr:sport_event:27977202",  # 2022-01-27 | Saudi Arabia vs Oman
        "sr:sport_event:20718103",  # 2022-01-27 | Ecuador vs Brazil
        "sr:sport_event:20718101",  # 2022-01-27 | Paraguay vs Uruguay
        "sr:sport_event:27747546",  # 2022-01-28 | Costa Rica vs Panama
        "sr:sport_event:20718097",  # 2022-01-28 | Colombia vs Peru
        "sr:sport_event:20718095",  # 2022-01-28 | Chile vs Argentina
        "sr:sport_event:27747548",  # 2022-01-28 | Jamaica vs Mexico
        "sr:sport_event:27747542",  # 2022-01-28 | Honduras vs Canada
        "sr:sport_event:31406225",  # 2022-01-29 | Burkina Faso vs Tunisia
        "sr:sport_event:31406235",  # 2022-01-30 | Egypt vs Morocco
        "sr:sport_event:31406223",  # 2022-01-30 | Senegal vs Equatorial Guinea
        "sr:sport_event:27747550",  # 2022-01-30 | Canada vs USA
        "sr:sport_event:27747556",  # 2022-01-30 | Panama vs Jamaica
        "sr:sport_event:27747554",  # 2022-01-30 | Mexico vs Costa Rica
        "sr:sport_event:20718113",  # 2022-02-01 | Argentina vs Colombia
        "sr:sport_event:20718111",  # 2022-02-01 | Uruguay vs Venezuela
        "sr:sport_event:27976672",  # 2022-02-01 | Lebanon vs Iraq
        "sr:sport_event:27977222",  # 2022-02-01 | Japan vs Saudi Arabia
        "sr:sport_event:27977226",  # 2022-02-01 | Oman vs Australia
        "sr:sport_event:20718107",  # 2022-02-02 | Brazil vs Paraguay
        "sr:sport_event:20718109",  # 2022-02-02 | Peru vs Ecuador
        "sr:sport_event:31406233",  # 2022-02-02 | Burkina Faso vs Senegal
        "sr:sport_event:30675433",  # 2022-03-24 | Sweden vs Czechia
        "sr:sport_event:20718119",  # 2022-03-24 | Colombia vs Bolivia
        "sr:sport_event:20718117",  # 2022-03-24 | Brazil vs Chile
        "sr:sport_event:20718115",  # 2022-03-24 | Paraguay vs Ecuador
        "sr:sport_event:20718121",  # 2022-03-24 | Uruguay vs Peru
        "sr:sport_event:30675429",  # 2022-03-24 | Wales vs Austria
        "sr:sport_event:30675437",  # 2022-03-24 | Portugal vs Turkiye
        "sr:sport_event:32528975",  # 2022-03-24 | New Zealand vs New Caledonia
        "sr:sport_event:27976678",  # 2022-03-24 | Iraq vs United Arab Emirates
        "sr:sport_event:27977230",  # 2022-03-24 | China PR vs Saudi Arabia
        "sr:sport_event:27977232",  # 2022-03-24 | Australia vs Japan
        "sr:sport_event:30675427",  # 2022-03-24 | Scotland vs Ukraine
        "sr:sport_event:20718123",  # 2022-03-25 | Argentina vs Venezuela
        "sr:sport_event:31716241",  # 2022-03-25 | Egypt vs Senegal
        "sr:sport_event:31716245",  # 2022-03-25 | Ghana vs Nigeria
        "sr:sport_event:31716249",  # 2022-03-25 | Mali vs Tunisia
        "sr:sport_event:31716243",  # 2022-03-25 | Cameroon vs Algeria
        "sr:sport_event:31716247",  # 2022-03-25 | Congo DR vs Morocco
        "sr:sport_event:27747566",  # 2022-03-25 | Costa Rica vs Canada
        "sr:sport_event:27747572",  # 2022-03-25 | Mexico vs USA
        "sr:sport_event:27747568",  # 2022-03-25 | Panama vs Honduras
        "sr:sport_event:27747580",  # 2022-03-27 | USA vs Panama
        "sr:sport_event:27747576",  # 2022-03-27 | Honduras vs Mexico
        "sr:sport_event:32861699",  # 2022-03-27 | New Zealand vs Tahiti
        "sr:sport_event:27747574",  # 2022-03-27 | Canada vs Jamaica
        "sr:sport_event:20718131",  # 2022-03-29 | Bolivia vs Brazil
        "sr:sport_event:20718129",  # 2022-03-29 | Venezuela vs Colombia
        "sr:sport_event:20718127",  # 2022-03-29 | Peru vs Paraguay
        "sr:sport_event:20718125",  # 2022-03-29 | Ecuador vs Argentina
        "sr:sport_event:20718133",  # 2022-03-29 | Chile vs Uruguay
        "sr:sport_event:31716257",  # 2022-03-29 | Morocco vs Congo DR
        "sr:sport_event:31716253",  # 2022-03-29 | Algeria vs Cameroon
        "sr:sport_event:32863301",  # 2022-03-29 | Poland vs Sweden
        "sr:sport_event:32862819",  # 2022-03-29 | Portugal vs North Macedonia
        "sr:sport_event:27977238",  # 2022-03-29 | Saudi Arabia vs Australia
        "sr:sport_event:31716255",  # 2022-03-29 | Nigeria vs Ghana
        "sr:sport_event:31716259",  # 2022-03-29 | Tunisia vs Mali
        "sr:sport_event:31716251",  # 2022-03-29 | Senegal vs Egypt
        "sr:sport_event:27976682",  # 2022-03-29 | Syria vs Iraq
        "sr:sport_event:27977236",  # 2022-03-29 | Japan vs Vietnam
        "sr:sport_event:32901503",  # 2022-03-30 | Solomon Islands vs New Zealand
        "sr:sport_event:39732249",  # 2023-03-23 | Ghana vs Angola
        "sr:sport_event:36601835",  # 2023-03-23 | Italy vs England
        "sr:sport_event:36604645",  # 2023-03-23 | Portugal vs Liechtenstein
        "sr:sport_event:36604649",  # 2023-03-23 | Bosnia and Herzegovina vs Iceland
        "sr:sport_event:39732333",  # 2023-03-23 | Algeria vs Niger
        "sr:sport_event:36601339",  # 2023-03-24 | France vs Netherlands
        "sr:sport_event:36602927",  # 2023-03-24 | Austria vs Azerbaijan
        "sr:sport_event:36602925",  # 2023-03-24 | Sweden vs Belgium
        "sr:sport_event:39732749",  # 2023-03-24 | Senegal vs Mozambique
        "sr:sport_event:39732745",  # 2023-03-24 | Tunisia vs Libya
        "sr:sport_event:39706823",  # 2023-03-24 | Cape Verde vs Eswatini
        "sr:sport_event:33313873",  # 2023-03-24 | Suriname vs Mexico
        "sr:sport_event:39732241",  # 2023-03-24 | Egypt vs Malawi
        "sr:sport_event:33825135",  # 2023-03-24 | South Africa vs Liberia
        "sr:sport_event:33824947",  # 2023-03-24 | Ivory Coast vs Comoros
        "sr:sport_event:36600909",  # 2023-03-25 | Scotland vs Cyprus
        "sr:sport_event:36604337",  # 2023-03-25 | Belarus vs Switzerland
        "sr:sport_event:36600911",  # 2023-03-25 | Spain vs Norway
        "sr:sport_event:33314647",  # 2023-03-25 | Montserrat vs Haiti
        "sr:sport_event:36602317",  # 2023-03-25 | Croatia vs Wales
        "sr:sport_event:33314075",  # 2023-03-26 | Curacao vs Canada
        "sr:sport_event:36601837",  # 2023-03-26 | England vs Ukraine
        "sr:sport_event:36604711",  # 2023-03-26 | Luxembourg vs Portugal
        "sr:sport_event:36604713",  # 2023-03-26 | Slovakia vs Bosnia and Herzegovina
        "sr:sport_event:36602969",  # 2023-03-27 | Austria vs Estonia
        "sr:sport_event:36601429",  # 2023-03-27 | Ireland vs France
        "sr:sport_event:36602967",  # 2023-03-27 | Sweden vs Azerbaijan
        "sr:sport_event:33824839",  # 2023-03-27 | Niger vs Algeria
        "sr:sport_event:33824711",  # 2023-03-27 | Angola vs Ghana
        "sr:sport_event:33313877",  # 2023-03-27 | Mexico vs Jamaica
        "sr:sport_event:36601343",  # 2023-03-27 | Netherlands vs Gibraltar
        "sr:sport_event:33824307",  # 2023-03-28 | Eswatini vs Cape Verde
        "sr:sport_event:33824547",  # 2023-03-28 | Malawi vs Egypt
        "sr:sport_event:33825141",  # 2023-03-28 | Liberia vs South Africa
        "sr:sport_event:33825379",  # 2023-03-28 | Mozambique vs Senegal
        "sr:sport_event:36600917",  # 2023-03-28 | Georgia vs Norway
        "sr:sport_event:36600921",  # 2023-03-28 | Scotland vs Spain
        "sr:sport_event:36602319",  # 2023-03-28 | Turkiye vs Croatia
        "sr:sport_event:36604339",  # 2023-03-28 | Switzerland vs Israel
        "sr:sport_event:33824953",  # 2023-03-28 | Comoros vs Ivory Coast
        "sr:sport_event:33825103",  # 2023-03-28 | Libya vs Tunisia
        "sr:sport_event:33314653",  # 2023-03-28 | Haiti vs Bermuda
        "sr:sport_event:33824553",  # 2023-06-14 | Guinea vs Egypt
        "sr:sport_event:38916795",  # 2023-06-14 | Netherlands vs Croatia
        "sr:sport_event:38916797",  # 2023-06-15 | Spain vs Italy
        "sr:sport_event:40402153",  # 2023-06-15 | Panama vs Canada
        "sr:sport_event:40402209",  # 2023-06-16 | USA vs Mexico
        "sr:sport_event:36601433",  # 2023-06-16 | Gibraltar vs France
        "sr:sport_event:36601933",  # 2023-06-16 | Malta vs England
        "sr:sport_event:36604345",  # 2023-06-16 | Andorra vs Switzerland
        "sr:sport_event:33825383",  # 2023-06-17 | Benin vs Senegal
        "sr:sport_event:36604725",  # 2023-06-17 | Portugal vs Bosnia and Herzegovina
        "sr:sport_event:36602973",  # 2023-06-17 | Belgium vs Austria
        "sr:sport_event:36601013",  # 2023-06-17 | Norway vs Scotland
        "sr:sport_event:40806191",  # 2023-06-17 | Curacao vs Saint Kitts and Nevis
        "sr:sport_event:33825107",  # 2023-06-17 | Equatorial Guinea vs Tunisia
        "sr:sport_event:33824957",  # 2023-06-17 | Zambia vs Ivory Coast
        "sr:sport_event:33825147",  # 2023-06-17 | South Africa vs Morocco
        "sr:sport_event:41775407",  # 2023-06-18 | Croatia vs Spain
        "sr:sport_event:41781635",  # 2023-06-18 | Panama vs Mexico
        "sr:sport_event:33824315",  # 2023-06-18 | Cape Verde vs Burkina Faso
        "sr:sport_event:33824843",  # 2023-06-18 | Uganda vs Algeria
        "sr:sport_event:33824721",  # 2023-06-18 | Madagascar vs Ghana
        "sr:sport_event:41775405",  # 2023-06-18 | Netherlands vs Italy
        "sr:sport_event:36604439",  # 2023-06-19 | Switzerland vs Romania
        "sr:sport_event:41781641",  # 2023-06-19 | Canada vs USA
        "sr:sport_event:36601435",  # 2023-06-19 | France vs Greece
        "sr:sport_event:36601937",  # 2023-06-19 | England vs North Macedonia
        "sr:sport_event:36604747",  # 2023-06-20 | Iceland vs Portugal
        "sr:sport_event:36602977",  # 2023-06-20 | Estonia vs Belgium
        "sr:sport_event:36602975",  # 2023-06-20 | Austria vs Sweden
        "sr:sport_event:36601021",  # 2023-06-20 | Norway vs Cyprus
        "sr:sport_event:36604749",  # 2023-06-20 | Bosnia and Herzegovina vs Luxembourg
        "sr:sport_event:36601017",  # 2023-06-20 | Scotland vs Georgia
        "sr:sport_event:36601605",  # 2023-09-07 | Netherlands vs Greece
        "sr:sport_event:43073829",  # 2023-09-07 | Iraq vs India
        "sr:sport_event:33824729",  # 2023-09-07 | Ghana vs Central African Republic
        "sr:sport_event:36601521",  # 2023-09-07 | France vs Ireland
        "sr:sport_event:33824861",  # 2023-09-07 | Algeria vs Tanzania
        "sr:sport_event:33825113",  # 2023-09-07 | Tunisia vs Botswana
        "sr:sport_event:42290185",  # 2023-09-07 | Trinidad and Tobago vs Curacao
        "sr:sport_event:42824593",  # 2023-09-07 | Paraguay vs Peru
        "sr:sport_event:42824595",  # 2023-09-07 | Colombia vs Venezuela
        "sr:sport_event:36601109",  # 2023-09-08 | Cyprus vs Scotland
        "sr:sport_event:36602331",  # 2023-09-08 | Croatia vs Latvia
        "sr:sport_event:33824561",  # 2023-09-08 | Egypt vs Ethiopia
        "sr:sport_event:42290183",  # 2023-09-08 | Panama vs Martinique
        "sr:sport_event:42824599",  # 2023-09-08 | Argentina vs Ecuador
        "sr:sport_event:36601107",  # 2023-09-08 | Georgia vs Spain
        "sr:sport_event:42824603",  # 2023-09-09 | Brazil vs Bolivia
        "sr:sport_event:36602993",  # 2023-09-09 | Azerbaijan vs Belgium
        "sr:sport_event:36602423",  # 2023-09-11 | Armenia vs Croatia
        "sr:sport_event:36604803",  # 2023-09-11 | Portugal vs Luxembourg
        "sr:sport_event:36604801",  # 2023-09-11 | Iceland vs Bosnia and Herzegovina
        "sr:sport_event:42290193",  # 2023-09-11 | Martinique vs Curacao
        "sr:sport_event:42290191",  # 2023-09-11 | Guatemala vs Panama
        "sr:sport_event:36601113",  # 2023-09-12 | Spain vs Cyprus
        "sr:sport_event:36602995",  # 2023-09-12 | Belgium vs Estonia
        "sr:sport_event:36601111",  # 2023-09-12 | Norway vs Georgia
        "sr:sport_event:36602997",  # 2023-09-12 | Sweden vs Austria
        "sr:sport_event:42824605",  # 2023-09-12 | Bolivia vs Argentina
        "sr:sport_event:42824607",  # 2023-09-12 | Ecuador vs Uruguay
        "sr:sport_event:42824609",  # 2023-09-12 | Venezuela vs Paraguay
        "sr:sport_event:36604451",  # 2023-09-12 | Switzerland vs Andorra
        "sr:sport_event:43577453",  # 2023-10-12 | Bolivia vs Ecuador
        "sr:sport_event:42291385",  # 2023-10-12 | Suriname vs Haiti
        "sr:sport_event:43577457",  # 2023-10-12 | Colombia vs Uruguay
        "sr:sport_event:36604457",  # 2023-10-12 | Israel vs Switzerland
        "sr:sport_event:36602511",  # 2023-10-12 | Croatia vs Turkiye
        "sr:sport_event:36601201",  # 2023-10-12 | Cyprus vs Norway
        "sr:sport_event:43577463",  # 2023-10-12 | Argentina vs Paraguay
        "sr:sport_event:36601115",  # 2023-10-12 | Spain vs Scotland
        "sr:sport_event:36604831",  # 2023-10-13 | Liechtenstein vs Bosnia and Herzegovina
        "sr:sport_event:36604829",  # 2023-10-13 | Portugal vs Slovakia
        "sr:sport_event:36603019",  # 2023-10-13 | Austria vs Belgium
        "sr:sport_event:36601695",  # 2023-10-13 | Netherlands vs France
        "sr:sport_event:43577461",  # 2023-10-13 | Brazil vs Venezuela
        "sr:sport_event:36603079",  # 2023-10-16 | Belgium vs Sweden
        "sr:sport_event:36601783",  # 2023-10-16 | Greece vs Netherlands
        "sr:sport_event:36604835",  # 2023-10-16 | Bosnia and Herzegovina vs Portugal
        "sr:sport_event:36603043",  # 2023-10-16 | Azerbaijan vs Austria
        "sr:sport_event:42291443",  # 2023-10-16 | Haiti vs Jamaica
        "sr:sport_event:43577481",  # 2023-10-17 | Ecuador vs Colombia
        "sr:sport_event:43577479",  # 2023-10-17 | Paraguay vs Bolivia
        "sr:sport_event:44249838",  # 2023-10-17 | Morocco vs Liberia
        "sr:sport_event:36602259",  # 2023-10-17 | England vs Italy
        "sr:sport_event:44431568",  # 2023-11-15 | Israel vs Switzerland
        "sr:sport_event:44832256",  # 2023-11-16 | Venezuela vs Ecuador
        "sr:sport_event:36604941",  # 2023-11-16 | Liechtenstein vs Portugal
        "sr:sport_event:36604921",  # 2023-11-16 | Luxembourg vs Bosnia and Herzegovina
        "sr:sport_event:45043084",  # 2023-11-16 | Morocco vs Eritrea
        "sr:sport_event:45042990",  # 2023-11-16 | Cape Verde vs Angola
        "sr:sport_event:36603083",  # 2023-11-16 | Estonia vs Austria
        "sr:sport_event:36603081",  # 2023-11-16 | Azerbaijan vs Sweden
        "sr:sport_event:36601331",  # 2023-11-16 | Cyprus vs Spain
        "sr:sport_event:36601245",  # 2023-11-16 | Georgia vs Scotland
        "sr:sport_event:44659320",  # 2023-11-16 | Saudi Arabia vs Pakistan
        "sr:sport_event:45043428",  # 2023-11-16 | Algeria vs Somalia
        "sr:sport_event:44659108",  # 2023-11-16 | Qatar vs Afghanistan
        "sr:sport_event:45041608",  # 2023-11-16 | Egypt vs Djibouti
        "sr:sport_event:44659482",  # 2023-11-16 | Australia vs Bangladesh
        "sr:sport_event:44659134",  # 2023-11-16 | Japan vs Myanmar
        "sr:sport_event:42590833",  # 2023-11-16 | Tajikistan vs Jordan
        "sr:sport_event:42590787",  # 2023-11-16 | Turkmenistan vs Uzbekistan
        "sr:sport_event:44659308",  # 2023-11-16 | Iraq vs Indonesia
        "sr:sport_event:36602267",  # 2023-11-17 | England vs Malta
        "sr:sport_event:45043592",  # 2023-11-17 | Tunisia vs Sao Tome and Principe
        "sr:sport_event:45043408",  # 2023-11-17 | Ivory Coast vs Seychelles
        "sr:sport_event:45043688",  # 2023-11-17 | Ghana vs Madagascar
        "sr:sport_event:44832390",  # 2023-11-17 | Colombia vs Brazil
        "sr:sport_event:44832392",  # 2023-11-17 | Argentina vs Uruguay
        "sr:sport_event:44832802",  # 2023-11-17 | Chile vs Paraguay
        "sr:sport_event:45246918",  # 2023-11-17 | Costa Rica vs Panama
        "sr:sport_event:45246932",  # 2023-11-18 | Honduras vs Mexico
        "sr:sport_event:45043420",  # 2023-11-20 | Gambia vs Ivory Coast
        "sr:sport_event:36602311",  # 2023-11-20 | North Macedonia vs England
        "sr:sport_event:45043100",  # 2023-11-21 | Tanzania vs Morocco
        "sr:sport_event:36601829",  # 2023-11-21 | Greece vs France
        "sr:sport_event:36601831",  # 2023-11-21 | Gibraltar vs Netherlands
        "sr:sport_event:36604637",  # 2023-11-21 | Romania vs Switzerland
        "sr:sport_event:44832396",  # 2023-11-21 | Paraguay vs Colombia
        "sr:sport_event:44832398",  # 2023-11-21 | Uruguay vs Bolivia
        "sr:sport_event:44832452",  # 2023-11-21 | Ecuador vs Chile
        "sr:sport_event:45043784",  # 2023-11-21 | Comoros vs Ghana
        "sr:sport_event:36602737",  # 2023-11-21 | Croatia vs Armenia
        "sr:sport_event:45042782",  # 2023-11-21 | Togo vs Senegal
        "sr:sport_event:45043600",  # 2023-11-21 | Malawi vs Tunisia
        "sr:sport_event:42590835",  # 2023-11-21 | Jordan vs Saudi Arabia
        "sr:sport_event:45246920",  # 2023-11-21 | Panama vs Costa Rica
        "sr:sport_event:42590819",  # 2023-11-21 | Vietnam vs Iraq
        "sr:sport_event:45042950",  # 2023-11-21 | Rwanda vs South Africa
        "sr:sport_event:42590625",  # 2023-11-21 | India vs Qatar
        "sr:sport_event:42590735",  # 2023-11-21 | Syria vs Japan
        "sr:sport_event:42590881",  # 2023-11-21 | Palestine vs Australia
        "sr:sport_event:45043074",  # 2023-11-21 | Eswatini vs Cape Verde
        "sr:sport_event:42590789",  # 2023-11-21 | Uzbekistan vs IR Iran
        "sr:sport_event:42590821",  # 2024-03-21 | Iraq vs Philippines
        "sr:sport_event:42590837",  # 2024-03-21 | Saudi Arabia vs Tajikistan
        "sr:sport_event:48585821",  # 2024-03-21 | Cape Verde vs Guyana
        "sr:sport_event:46186193",  # 2024-03-21 | Portugal vs Sweden
        "sr:sport_event:47748371",  # 2024-03-21 | South Africa vs Andorra
        "sr:sport_event:45623330",  # 2024-03-21 | Bosnia and Herzegovina vs Ukraine
        "sr:sport_event:42590629",  # 2024-03-21 | Qatar vs Kuwait
        "sr:sport_event:42590883",  # 2024-03-21 | Australia vs Lebanon
        "sr:sport_event:42590737",  # 2024-03-21 | Japan vs Korea DPR
        "sr:sport_event:44659296",  # 2024-03-21 | Hong Kong vs Uzbekistan
        "sr:sport_event:44659324",  # 2024-03-21 | Pakistan vs Jordan
        "sr:sport_event:47105177",  # 2024-03-22 | Norway vs Czechia
        "sr:sport_event:48629209",  # 2024-03-22 | Senegal vs Gabon
        "sr:sport_event:46186281",  # 2024-03-22 | Netherlands vs Scotland
        "sr:sport_event:48700861",  # 2024-03-22 | Nigeria vs Ghana
        "sr:sport_event:45640774",  # 2024-03-22 | Panama vs Mexico
        "sr:sport_event:47748379",  # 2024-03-22 | Ecuador vs Guatemala
        "sr:sport_event:48661803",  # 2024-03-23 | Argentina vs El Salvador
        "sr:sport_event:48586403",  # 2024-03-25 | Cape Verde vs Equatorial Guinea
        "sr:sport_event:47748445",  # 2024-03-25 | Sweden vs Albania
        "sr:sport_event:48897079",  # 2024-03-25 | USA vs Mexico
        "sr:sport_event:48254431",  # 2024-03-25 | Russia vs Paraguay
        "sr:sport_event:42590635",  # 2024-03-26 | Kuwait vs Qatar
        "sr:sport_event:44659326",  # 2024-03-26 | Jordan vs Pakistan
        "sr:sport_event:46870049",  # 2024-03-26 | Romania vs Colombia
        "sr:sport_event:48526733",  # 2024-03-26 | Uruguay vs Ivory Coast
        "sr:sport_event:48845117",  # 2024-03-26 | Senegal vs Benin
        "sr:sport_event:46144951",  # 2024-03-26 | Germany vs Netherlands
        "sr:sport_event:46186339",  # 2024-03-26 | Scotland vs Northern Ireland
        "sr:sport_event:46186395",  # 2024-03-26 | England vs Belgium
        "sr:sport_event:47105499",  # 2024-03-26 | Ireland vs Switzerland
        "sr:sport_event:47731137",  # 2024-03-26 | Austria vs Turkiye
        "sr:sport_event:47395897",  # 2024-03-26 | France vs Chile
        "sr:sport_event:48934567",  # 2024-03-26 | Egypt vs Croatia
        "sr:sport_event:48934703",  # 2024-03-26 | New Zealand vs Tunisia
        "sr:sport_event:47105501",  # 2024-03-26 | Spain vs Brazil
        "sr:sport_event:47748531",  # 2024-03-26 | Algeria vs South Africa
        "sr:sport_event:48805989",  # 2024-03-26 | Morocco vs Mauritania
        "sr:sport_event:47395895",  # 2024-03-26 | Slovenia vs Portugal
        "sr:sport_event:47105495",  # 2024-03-26 | Norway vs Slovakia
        "sr:sport_event:42590739",  # 2024-03-26 | Korea DPR vs Japan
        "sr:sport_event:42590885",  # 2024-03-26 | Lebanon vs Australia
        "sr:sport_event:42590823",  # 2024-03-26 | Philippines vs Iraq
        "sr:sport_event:44659298",  # 2024-03-26 | Uzbekistan vs Hong Kong
        "sr:sport_event:48992925",  # 2024-03-26 | Ghana vs Uganda
        "sr:sport_event:42590839",  # 2024-03-26 | Tajikistan vs Saudi Arabia
        "sr:sport_event:47847923",  # 2024-06-05 | Belgium vs Montenegro
        "sr:sport_event:47463107",  # 2024-06-05 | Curacao vs Barbados
        "sr:sport_event:48219169",  # 2024-06-05 | Spain vs Andorra
        "sr:sport_event:50107161",  # 2024-06-05 | Tunisia vs Equatorial Guinea
        "sr:sport_event:49656447",  # 2024-06-05 | France vs Luxembourg
        "sr:sport_event:47847921",  # 2024-06-05 | Denmark vs Sweden
        "sr:sport_event:47847925",  # 2024-06-05 | Norway vs Kosovo
        "sr:sport_event:47463109",  # 2024-06-06 | Haiti vs Saint Lucia
        "sr:sport_event:48855937",  # 2024-06-06 | Mali vs Ghana
        "sr:sport_event:48855733",  # 2024-06-06 | Algeria vs Guinea
        "sr:sport_event:48855193",  # 2024-06-06 | Senegal vs Congo DR
        "sr:sport_event:48855051",  # 2024-06-06 | Egypt vs Burkina Faso
        "sr:sport_event:49441357",  # 2024-06-06 | Netherlands vs Canada
        "sr:sport_event:42590841",  # 2024-06-06 | Jordan vs Tajikistan
        "sr:sport_event:44659116",  # 2024-06-06 | Afghanistan vs Qatar
        "sr:sport_event:44659328",  # 2024-06-06 | Pakistan vs Saudi Arabia
        "sr:sport_event:42590795",  # 2024-06-06 | Uzbekistan vs Turkmenistan
        "sr:sport_event:44659142",  # 2024-06-06 | Myanmar vs Japan
        "sr:sport_event:44659548",  # 2024-06-06 | Bangladesh vs Australia
        "sr:sport_event:44659316",  # 2024-06-06 | Indonesia vs Iraq
        "sr:sport_event:49441353",  # 2024-06-06 | Mexico vs Uruguay
        "sr:sport_event:47463131",  # 2024-06-07 | Panama vs Guyana
        "sr:sport_event:50259853",  # 2024-06-08 | Peru vs Paraguay
        "sr:sport_event:47463113",  # 2024-06-09 | Aruba vs Curacao
        "sr:sport_event:49441451",  # 2024-06-09 | Mexico vs Brazil
        "sr:sport_event:48855989",  # 2024-06-10 | Ghana vs Central African Republic
        "sr:sport_event:49441603",  # 2024-06-10 | Netherlands vs Iceland
        "sr:sport_event:48855057",  # 2024-06-10 | Guinea-Bissau vs Egypt
        "sr:sport_event:47463135",  # 2024-06-10 | Montserrat vs Panama
        "sr:sport_event:48855739",  # 2024-06-10 | Uganda vs Algeria
        "sr:sport_event:47659487",  # 2024-10-10 | England vs Greece
        "sr:sport_event:47659383",  # 2024-10-10 | Israel vs France
        "sr:sport_event:47659385",  # 2024-10-10 | Italy vs Belgium
        "sr:sport_event:47659619",  # 2024-10-10 | Austria vs Kazakhstan
        "sr:sport_event:53624649",  # 2024-10-10 | Venezuela vs Argentina
        "sr:sport_event:51443485",  # 2024-10-10 | Algeria vs Togo
        "sr:sport_event:53624645",  # 2024-10-10 | Bolivia vs Colombia
        "sr:sport_event:53624647",  # 2024-10-10 | Ecuador vs Paraguay
        "sr:sport_event:47659623",  # 2024-10-10 | Norway vs Slovenia
        "sr:sport_event:51133409",  # 2024-10-10 | Iraq vs Palestine
        "sr:sport_event:51133473",  # 2024-10-10 | Australia vs China PR
        "sr:sport_event:51133471",  # 2024-10-10 | Saudi Arabia vs Japan
        "sr:sport_event:51133407",  # 2024-10-10 | Jordan vs Korea Republic
        "sr:sport_event:51133343",  # 2024-10-10 | Uzbekistan vs IR Iran
        "sr:sport_event:51133345",  # 2024-10-10 | Qatar vs Kyrgyzstan
        "sr:sport_event:51442887",  # 2024-10-10 | Cape Verde vs Botswana
        "sr:sport_event:51443979",  # 2024-10-10 | Ghana vs Sudan
        "sr:sport_event:51442889",  # 2024-10-11 | Egypt vs Mauritania
        "sr:sport_event:51444121",  # 2024-10-11 | South Africa vs Congo Republic
        "sr:sport_event:53433411",  # 2024-10-11 | New Zealand vs Tahiti
        "sr:sport_event:53624651",  # 2024-10-11 | Chile vs Brazil
        "sr:sport_event:50851703",  # 2024-10-12 | Aruba vs Haiti
        "sr:sport_event:53624653",  # 2024-10-12 | Peru vs Uruguay
        "sr:sport_event:51421039",  # 2024-10-13 | USA vs Panama
        "sr:sport_event:54461133",  # 2024-10-13 | Mexico vs Valencia CF
        "sr:sport_event:50851679",  # 2024-10-14 | Curacao vs Grenada
        "sr:sport_event:47659805",  # 2024-10-14 | Estonia vs Sweden
        "sr:sport_event:47659413",  # 2024-10-14 | Germany vs Netherlands
        "sr:sport_event:47659411",  # 2024-10-14 | Bosnia and Herzegovina vs Hungary
        "sr:sport_event:47659387",  # 2024-10-14 | Belgium vs France
        "sr:sport_event:51443489",  # 2024-10-14 | Togo vs Algeria
        "sr:sport_event:54183571",  # 2024-10-14 | New Zealand vs Malaysia
        "sr:sport_event:51133413",  # 2024-10-15 | Jordan vs Oman
        "sr:sport_event:51442891",  # 2024-10-15 | Botswana vs Cape Verde
        "sr:sport_event:51442893",  # 2024-10-15 | Mauritania vs Egypt
        "sr:sport_event:51444015",  # 2024-10-15 | Sierra Leone vs Ivory Coast
        "sr:sport_event:51444125",  # 2024-10-15 | Congo Republic vs South Africa
        "sr:sport_event:51133477",  # 2024-10-15 | Saudi Arabia vs Bahrain
        "sr:sport_event:51133347",  # 2024-10-15 | IR Iran vs Qatar
        "sr:sport_event:47659353",  # 2024-10-15 | Poland vs Croatia
        "sr:sport_event:47659355",  # 2024-10-15 | Scotland vs Portugal
        "sr:sport_event:47659439",  # 2024-10-15 | Spain vs Serbia
        "sr:sport_event:47659441",  # 2024-10-15 | Switzerland vs Denmark
        "sr:sport_event:51441989",  # 2024-10-15 | Comoros vs Tunisia
        "sr:sport_event:51442391",  # 2024-10-15 | Central African Republic vs Morocco
        "sr:sport_event:53624655",  # 2024-10-15 | Colombia vs Chile
        "sr:sport_event:51133475",  # 2024-10-15 | Japan vs Australia
        "sr:sport_event:51133411",  # 2024-10-15 | Korea Republic vs Iraq
        "sr:sport_event:51444159",  # 2024-10-15 | Malawi vs Senegal
        "sr:sport_event:51133349",  # 2024-10-15 | Uzbekistan vs United Arab Emirates
        "sr:sport_event:50851707",  # 2024-10-15 | Haiti vs Aruba
        "sr:sport_event:51443983",  # 2024-10-15 | Sudan vs Ghana
        "sr:sport_event:47659391",  # 2024-11-14 | Belgium vs Italy
        "sr:sport_event:47659393",  # 2024-11-14 | France vs Israel
        "sr:sport_event:54504391",  # 2024-11-14 | Paraguay vs Argentina
        "sr:sport_event:47659639",  # 2024-11-14 | Slovenia vs Norway
        "sr:sport_event:54622891",  # 2024-11-14 | Venezuela vs Brazil
        "sr:sport_event:51444163",  # 2024-11-14 | Burkina Faso vs Senegal
        "sr:sport_event:47659495",  # 2024-11-14 | Greece vs England
        "sr:sport_event:51441993",  # 2024-11-14 | Madagascar vs Tunisia
        "sr:sport_event:51133417",  # 2024-11-14 | Iraq vs Jordan
        "sr:sport_event:51133353",  # 2024-11-14 | Qatar vs Uzbekistan
        "sr:sport_event:47659635",  # 2024-11-14 | Kazakhstan vs Austria
        "sr:sport_event:51443493",  # 2024-11-14 | Equatorial Guinea vs Algeria
        "sr:sport_event:51133481",  # 2024-11-14 | Australia vs Saudi Arabia
        "sr:sport_event:51442395",  # 2024-11-15 | Gabon vs Morocco
        "sr:sport_event:51443987",  # 2024-11-15 | Angola vs Ghana
        "sr:sport_event:47659443",  # 2024-11-15 | Denmark vs Spain
        "sr:sport_event:47659445",  # 2024-11-15 | Switzerland vs Serbia
        "sr:sport_event:47659357",  # 2024-11-15 | Portugal vs Poland
        "sr:sport_event:47659359",  # 2024-11-15 | Scotland vs Croatia
        "sr:sport_event:51133485",  # 2024-11-15 | Indonesia vs Japan
        "sr:sport_event:51444019",  # 2024-11-15 | Zambia vs Ivory Coast
        "sr:sport_event:51442897",  # 2024-11-15 | Cape Verde vs Egypt
        "sr:sport_event:51444143",  # 2024-11-15 | Uganda vs South Africa
        "sr:sport_event:53433441",  # 2024-11-15 | New Zealand vs Vanuatu
        "sr:sport_event:54669121",  # 2024-11-15 | Costa Rica vs Panama
        "sr:sport_event:54622885",  # 2024-11-15 | Ecuador vs Bolivia
        "sr:sport_event:54622887",  # 2024-11-16 | Uruguay vs Colombia
        "sr:sport_event:54669127",  # 2024-11-16 | Honduras vs Mexico
        "sr:sport_event:51441995",  # 2024-11-18 | Tunisia vs Gambia
        "sr:sport_event:47659449",  # 2024-11-18 | Spain vs Switzerland
        "sr:sport_event:50851687",  # 2024-11-18 | Curacao vs Saint Lucia
        "sr:sport_event:47659363",  # 2024-11-18 | Poland vs Scotland
        "sr:sport_event:47659361",  # 2024-11-18 | Croatia vs Portugal
        "sr:sport_event:51442397",  # 2024-11-18 | Morocco vs Lesotho
        "sr:sport_event:51443989",  # 2024-11-18 | Ghana vs Niger
        "sr:sport_event:53437569",  # 2024-11-18 | Samoa vs New Zealand
        "sr:sport_event:51133425",  # 2024-11-19 | Kuwait vs Jordan
        "sr:sport_event:51444165",  # 2024-11-19 | Senegal vs Burundi
        "sr:sport_event:47659419",  # 2024-11-19 | Bosnia and Herzegovina vs Netherlands
        "sr:sport_event:47659421",  # 2024-11-19 | Hungary vs Germany
        "sr:sport_event:47659813",  # 2024-11-19 | Sweden vs Azerbaijan
        "sr:sport_event:54622931",  # 2024-11-19 | Bolivia vs Paraguay
        "sr:sport_event:54622933",  # 2024-11-19 | Colombia vs Ecuador
        "sr:sport_event:51133487",  # 2024-11-19 | Bahrain vs Australia
        "sr:sport_event:51444131",  # 2024-11-19 | South Africa vs South Sudan
        "sr:sport_event:51133423",  # 2024-11-19 | Oman vs Iraq
        "sr:sport_event:50851715",  # 2024-11-19 | Haiti vs Puerto Rico
        "sr:sport_event:54669131",  # 2024-11-19 | Panama vs Costa Rica
        "sr:sport_event:51133361",  # 2024-11-19 | Korea DPR vs Uzbekistan
        "sr:sport_event:51133489",  # 2024-11-19 | Indonesia vs Saudi Arabia
        "sr:sport_event:51133491",  # 2024-11-19 | China PR vs Japan
        "sr:sport_event:51442899",  # 2024-11-19 | Egypt vs Botswana
        "sr:sport_event:51444021",  # 2024-11-19 | Ivory Coast vs Chad
        "sr:sport_event:51442901",  # 2024-11-19 | Mauritania vs Cape Verde
        "sr:sport_event:51133359",  # 2024-11-19 | United Arab Emirates vs Qatar
        "sr:sport_event:51133497",  # 2025-03-20 | Saudi Arabia vs China PR
        "sr:sport_event:55807517",  # 2025-03-20 | Ukraine vs Belgium
        "sr:sport_event:55807521",  # 2025-03-20 | Austria vs Serbia
        "sr:sport_event:55807529",  # 2025-03-20 | Greece vs Scotland
        "sr:sport_event:55807539",  # 2025-03-20 | Netherlands vs Spain
        "sr:sport_event:55623887",  # 2025-03-20 | Paraguay vs Chile
        "sr:sport_event:55807549",  # 2025-03-20 | Croatia vs France
        "sr:sport_event:55807555",  # 2025-03-20 | Italy vs Germany
        "sr:sport_event:55753913",  # 2025-03-20 | USA vs Panama
        "sr:sport_event:51133433",  # 2025-03-20 | Jordan vs Palestine
        "sr:sport_event:55807543",  # 2025-03-20 | Denmark vs Portugal
        "sr:sport_event:51133431",  # 2025-03-20 | Iraq vs Kuwait
        "sr:sport_event:51133495",  # 2025-03-20 | Australia vs Indonesia
        "sr:sport_event:51133493",  # 2025-03-20 | Japan vs Bahrain
        "sr:sport_event:51133367",  # 2025-03-20 | Qatar vs Korea DPR
        "sr:sport_event:48855439",  # 2025-03-20 | Cape Verde vs Mauritius
        "sr:sport_event:51133369",  # 2025-03-20 | Uzbekistan vs Kyrgyzstan
        "sr:sport_event:48855761",  # 2025-03-21 | Botswana vs Algeria
        "sr:sport_event:55731571",  # 2025-03-21 | New Zealand vs Fiji
        "sr:sport_event:55753911",  # 2025-03-21 | Canada vs Mexico
        "sr:sport_event:55623885",  # 2025-03-21 | Brazil vs Colombia
        "sr:sport_event:48855375",  # 2025-03-21 | South Africa vs Lesotho
        "sr:sport_event:48855803",  # 2025-03-24 | Tunisia vs Malawi
        "sr:sport_event:56418581",  # 2025-03-24 | Bosnia and Herzegovina vs Cyprus
        "sr:sport_event:48856109",  # 2025-03-24 | Madagascar vs Ghana
        "sr:sport_event:48855713",  # 2025-03-24 | Ivory Coast vs Gambia
        "sr:sport_event:56418703",  # 2025-03-24 | England vs Latvia
        "sr:sport_event:59148799",  # 2025-03-24 | New Caledonia vs New Zealand
        "sr:sport_event:59137579",  # 2025-03-24 | Mexico vs Panama
        "sr:sport_event:51133437",  # 2025-03-25 | Palestine vs Iraq
        "sr:sport_event:58593775",  # 2025-03-25 | Sweden vs Northern Ireland
        "sr:sport_event:48855625",  # 2025-03-25 | Morocco vs Tanzania
        "sr:sport_event:56418621",  # 2025-03-25 | Israel vs Norway
        "sr:sport_event:58593779",  # 2025-03-25 | Switzerland vs Luxembourg
        "sr:sport_event:55623917",  # 2025-03-25 | Bolivia vs Uruguay
        "sr:sport_event:48855221",  # 2025-03-25 | Senegal vs Togo
        "sr:sport_event:48855767",  # 2025-03-25 | Algeria vs Mozambique
        "sr:sport_event:48855079",  # 2025-03-25 | Egypt vs Sierra Leone
        "sr:sport_event:51133499",  # 2025-03-25 | Japan vs Saudi Arabia
        "sr:sport_event:51133435",  # 2025-03-25 | Korea Republic vs Jordan
        "sr:sport_event:51133501",  # 2025-03-25 | China PR vs Australia
        "sr:sport_event:51133373",  # 2025-03-25 | Kyrgyzstan vs Qatar
        "sr:sport_event:48855385",  # 2025-03-25 | Benin vs South Africa
        "sr:sport_event:48855451",  # 2025-03-25 | Angola vs Cape Verde
        "sr:sport_event:51133371",  # 2025-03-25 | IR Iran vs Uzbekistan
        "sr:sport_event:60376735",  # 2025-06-05 | Paraguay vs Uruguay
        "sr:sport_event:55809539",  # 2025-06-05 | Spain vs France
        "sr:sport_event:51133441",  # 2025-06-05 | Iraq vs Korea Republic
        "sr:sport_event:51133377",  # 2025-06-05 | Qatar vs IR Iran
        "sr:sport_event:60376737",  # 2025-06-05 | Ecuador vs Brazil
        "sr:sport_event:60922789",  # 2025-06-05 | Algeria vs Rwanda
        "sr:sport_event:51133443",  # 2025-06-05 | Oman vs Jordan
        "sr:sport_event:51133379",  # 2025-06-05 | United Arab Emirates vs Uzbekistan
        "sr:sport_event:51133505",  # 2025-06-05 | Australia vs Japan
        "sr:sport_event:51133507",  # 2025-06-05 | Bahrain vs Saudi Arabia
        "sr:sport_event:56418793",  # 2025-06-06 | Gibraltar vs Croatia
        "sr:sport_event:56418665",  # 2025-06-06 | North Macedonia vs Belgium
        "sr:sport_event:60698921",  # 2025-06-06 | Scotland vs Iceland
        "sr:sport_event:60698923",  # 2025-06-06 | Ireland vs Senegal
        "sr:sport_event:56418627",  # 2025-06-06 | Norway vs Italy
        "sr:sport_event:61037745",  # 2025-06-06 | South Africa vs Tanzania
        "sr:sport_event:60376739",  # 2025-06-06 | Chile vs Argentina
        "sr:sport_event:60698919",  # 2025-06-06 | Hungary vs Sweden
        "sr:sport_event:55809543",  # 2025-06-08 | Germany vs France
        "sr:sport_event:47463195",  # 2025-06-08 | Belize vs Panama
        "sr:sport_event:61037747",  # 2025-06-09 | Algeria vs Rwanda
        "sr:sport_event:60453207",  # 2025-06-09 | Liechtenstein vs Scotland
        "sr:sport_event:56418629",  # 2025-06-09 | Estonia vs Norway
        "sr:sport_event:56418671",  # 2025-06-09 | Belgium vs Wales
        "sr:sport_event:56418797",  # 2025-06-09 | Croatia vs Czechia
        "sr:sport_event:61013891",  # 2025-06-09 | Morocco vs Benin
        "sr:sport_event:51133449",  # 2025-06-10 | Jordan vs Iraq
        "sr:sport_event:51133513",  # 2025-06-10 | Saudi Arabia vs Australia
        "sr:sport_event:56418751",  # 2025-06-10 | Netherlands vs Malta
        "sr:sport_event:59321973",  # 2025-06-10 | New Zealand vs Ukraine
        "sr:sport_event:47463127",  # 2025-06-10 | Haiti vs Curacao
        "sr:sport_event:60376747",  # 2025-06-10 | Uruguay vs Venezuela
        "sr:sport_event:60453215",  # 2025-06-10 | Sweden vs Algeria
        "sr:sport_event:60454813",  # 2025-06-10 | England vs Senegal
        "sr:sport_event:56418591",  # 2025-06-10 | San Marino vs Austria
        "sr:sport_event:60453205",  # 2025-06-10 | Slovenia vs Bosnia and Herzegovina
        "sr:sport_event:60768249",  # 2025-06-10 | South Africa vs Mauritius
        "sr:sport_event:51133385",  # 2025-06-10 | Uzbekistan vs Qatar
        "sr:sport_event:51133511",  # 2025-06-10 | Japan vs Indonesia
        "sr:sport_event:62282194",  # 2025-09-04 | Suriname vs Panama
        "sr:sport_event:56418457",  # 2025-09-04 | Slovakia vs Germany
        "sr:sport_event:48855205",  # 2025-09-04 | Tunisia vs Liberia
        "sr:sport_event:48855191",  # 2025-09-04 | Algeria vs Botswana
        "sr:sport_event:56418755",  # 2025-09-04 | Netherlands vs Poland
        "sr:sport_event:56418675",  # 2025-09-04 | Liechtenstein vs Belgium
        "sr:sport_event:56418531",  # 2025-09-04 | Bulgaria vs Spain
        "sr:sport_event:48855085",  # 2025-09-04 | Mauritius vs Cape Verde
        "sr:sport_event:60525655",  # 2025-09-04 | Norway vs Finland
        "sr:sport_event:63327615",  # 2025-09-04 | Saudi Arabia vs North Macedonia
        "sr:sport_event:48855211",  # 2025-09-04 | Chad vs Ghana
        "sr:sport_event:62884713",  # 2025-09-04 | Iraq vs Hong Kong
        "sr:sport_event:62629619",  # 2025-09-04 | Russia vs Jordan
        "sr:sport_event:48855063",  # 2025-09-05 | Lesotho vs South Africa
        "sr:sport_event:63295465",  # 2025-09-05 | Australia vs New Zealand
        "sr:sport_event:61964220",  # 2025-09-05 | Brazil vs Chile
        "sr:sport_event:62282418",  # 2025-09-06 | Haiti vs Honduras
        "sr:sport_event:62282300",  # 2025-09-06 | Trinidad and Tobago vs Curacao
        "sr:sport_event:63293275",  # 2025-09-07 | Mexico vs Japan
        "sr:sport_event:48855469",  # 2025-09-08 | Ghana vs Mali
        "sr:sport_event:56418805",  # 2025-09-08 | Croatia vs Montenegro
        "sr:sport_event:56418485",  # 2025-09-08 | Belarus vs Scotland
        "sr:sport_event:56418323",  # 2025-09-08 | Kosovo vs Sweden
        "sr:sport_event:63073203",  # 2025-09-08 | Czechia vs Saudi Arabia
        "sr:sport_event:56418325",  # 2025-09-08 | Switzerland vs Slovenia
        "sr:sport_event:48855441",  # 2025-09-08 | Guinea vs Algeria
        "sr:sport_event:48855453",  # 2025-09-08 | Equatorial Guinea vs Tunisia
        "sr:sport_event:48855419",  # 2025-09-08 | Zambia vs Morocco
        "sr:sport_event:63556427",  # 2025-09-09 | Jordan vs Dominican Republic
        "sr:sport_event:56418719",  # 2025-09-09 | Serbia vs England
        "sr:sport_event:63556431",  # 2025-09-09 | Egypt vs Tunisia
        "sr:sport_event:56418511",  # 2025-09-09 | France vs Iceland
        "sr:sport_event:56418559",  # 2025-09-09 | Hungary vs Portugal
        "sr:sport_event:56418597",  # 2025-09-09 | Bosnia and Herzegovina vs Austria
        "sr:sport_event:56418639",  # 2025-09-09 | Norway vs Moldova
        "sr:sport_event:60698957",  # 2025-09-09 | Wales vs Canada
        "sr:sport_event:48855429",  # 2025-09-09 | Gabon vs Ivory Coast
        "sr:sport_event:48855347",  # 2025-09-09 | Cape Verde vs Cameroon
        "sr:sport_event:62282200",  # 2025-09-09 | Panama vs Guatemala
        "sr:sport_event:63295473",  # 2025-09-09 | New Zealand vs Australia
        "sr:sport_event:48855227",  # 2025-09-09 | Burkina Faso vs Egypt
        "sr:sport_event:48855313",  # 2025-09-09 | Congo DR vs Senegal
        "sr:sport_event:48855325",  # 2025-09-09 | South Africa vs Nigeria
        "sr:sport_event:56418807",  # 2025-10-09 | Czechia vs Croatia
        "sr:sport_event:64032833",  # 2025-10-09 | Morocco vs Bahrain
        "sr:sport_event:63295841",  # 2025-10-09 | Poland vs New Zealand
        "sr:sport_event:56418763",  # 2025-10-09 | Malta vs Netherlands
        "sr:sport_event:60525673",  # 2025-10-09 | England vs Wales
        "sr:sport_event:56418601",  # 2025-10-09 | Austria vs San Marino
        "sr:sport_event:56418491",  # 2025-10-09 | Scotland vs Greece
        "sr:sport_event:48855529",  # 2025-10-09 | Somalia vs Algeria
        "sr:sport_event:64213853",  # 2025-10-09 | Uzbekistan vs Kuwait
        "sr:sport_event:56418603",  # 2025-10-09 | Cyprus vs Bosnia and Herzegovina
        "sr:sport_event:64095037",  # 2025-10-10 | Bolivia vs Jordan
        "sr:sport_event:48855499",  # 2025-10-10 | Zimbabwe vs South Africa
        "sr:sport_event:48855515",  # 2025-10-10 | Seychelles vs Ivory Coast
        "sr:sport_event:48855491",  # 2025-10-10 | South Sudan vs Senegal
        "sr:sport_event:64033879",  # 2025-10-10 | Uruguay vs Dominican Republic
        "sr:sport_event:64008403",  # 2025-10-10 | Korea Republic vs Brazil
        "sr:sport_event:63298569",  # 2025-10-10 | Japan vs Paraguay
        "sr:sport_event:62282428",  # 2025-10-10 | Nicaragua vs Haiti
        "sr:sport_event:48855535",  # 2025-10-10 | Sao Tome and Principe vs Tunisia
        "sr:sport_event:63293753",  # 2025-10-11 | USA vs Ecuador
        "sr:sport_event:64095899",  # 2025-10-11 | Argentina vs Venezuela
        "sr:sport_event:62282206",  # 2025-10-11 | El Salvador vs Panama
        "sr:sport_event:63298593",  # 2025-10-12 | Mexico vs Colombia
        "sr:sport_event:56418331",  # 2025-10-13 | Slovenia vs Switzerland
        "sr:sport_event:56418517",  # 2025-10-13 | Iceland vs France
        "sr:sport_event:56418467",  # 2025-10-13 | Northern Ireland vs Germany
        "sr:sport_event:56418333",  # 2025-10-13 | Sweden vs Kosovo
        "sr:sport_event:56418687",  # 2025-10-13 | Wales vs Belgium
        "sr:sport_event:48855613",  # 2025-10-13 | Tunisia vs Namibia
        "sr:sport_event:64095149",  # 2025-10-13 | Uzbekistan vs Uruguay
        "sr:sport_event:48855575",  # 2025-10-13 | Cape Verde vs Eswatini
        "sr:sport_event:62092970",  # 2025-10-14 | Qatar vs United Arab Emirates
        "sr:sport_event:63883105",  # 2025-10-14 | Albania vs Jordan
        "sr:sport_event:62092982",  # 2025-10-14 | Saudi Arabia vs Iraq
        "sr:sport_event:56418567",  # 2025-10-14 | Portugal vs Hungary
        "sr:sport_event:56418727",  # 2025-10-14 | Latvia vs England
        "sr:sport_event:48855585",  # 2025-10-14 | Morocco vs Congo Republic
        "sr:sport_event:48855593",  # 2025-10-14 | Ivory Coast vs Kenya
        "sr:sport_event:48855687",  # 2025-10-14 | Senegal vs Mauritania
        "sr:sport_event:62282312",  # 2025-10-14 | Curacao vs Trinidad and Tobago
        "sr:sport_event:56418543",  # 2025-10-14 | Spain vs Bulgaria
        "sr:sport_event:60698967",  # 2025-10-14 | Norway vs New Zealand
        "sr:sport_event:62282432",  # 2025-10-14 | Honduras vs Haiti
        "sr:sport_event:63309071",  # 2025-10-14 | Japan vs Brazil
        "sr:sport_event:64096273",  # 2025-10-14 | Korea Republic vs Paraguay
        "sr:sport_event:48855567",  # 2025-10-14 | South Africa vs Rwanda
        "sr:sport_event:48855603",  # 2025-10-14 | Algeria vs Uganda
        "sr:sport_event:56418571",  # 2025-11-13 | Ireland vs Portugal
        "sr:sport_event:56418523",  # 2025-11-13 | France vs Ukraine
        "sr:sport_event:56418649",  # 2025-11-13 | Norway vs Estonia
        "sr:sport_event:65200712",  # 2025-11-13 | Algeria vs Zimbabwe
        "sr:sport_event:56418731",  # 2025-11-13 | England vs Serbia
        "sr:sport_event:64550264",  # 2025-11-13 | United Arab Emirates vs Iraq
        "sr:sport_event:65204782",  # 2025-11-13 | Cape Verde vs IR Iran
        "sr:sport_event:65200970",  # 2025-11-14 | Saudi Arabia vs Ivory Coast
        "sr:sport_event:65049860",  # 2025-11-14 | Tunisia vs Jordan
        "sr:sport_event:65204784",  # 2025-11-14 | Uzbekistan vs Egypt
        "sr:sport_event:65214510",  # 2025-11-14 | Morocco vs Mozambique
        "sr:sport_event:56418471",  # 2025-11-14 | Luxembourg vs Germany
        "sr:sport_event:56418771",  # 2025-11-14 | Poland vs Netherlands
        "sr:sport_event:56418817",  # 2025-11-14 | Croatia vs Faroe Islands
        "sr:sport_event:65107084",  # 2025-11-14 | Angola vs Argentina
        "sr:sport_event:62282316",  # 2025-11-14 | Bermuda vs Curacao
        "sr:sport_event:65201486",  # 2025-11-14 | Canada vs Ecuador
        "sr:sport_event:62282282",  # 2025-11-14 | Guatemala vs Panama
        "sr:sport_event:65202000",  # 2025-11-14 | Japan vs Ghana
        "sr:sport_event:62282436",  # 2025-11-14 | Haiti vs Costa Rica
        "sr:sport_event:65215442",  # 2025-11-15 | Colombia vs Australia
        "sr:sport_event:65214560",  # 2025-11-15 | Venezuela vs Australia
        "sr:sport_event:65216300",  # 2025-11-16 | Mexico vs Uruguay
        "sr:sport_event:65216304",  # 2025-11-16 | Colombia vs New Zealand
        "sr:sport_event:65764842",  # 2025-11-17 | Cape Verde vs Egypt
        "sr:sport_event:65688054",  # 2025-11-17 | Qatar vs Zimbabwe
        "sr:sport_event:56418477",  # 2025-11-17 | Germany vs Slovakia
        "sr:sport_event:56418775",  # 2025-11-17 | Netherlands vs Lithuania
        "sr:sport_event:56418821",  # 2025-11-17 | Montenegro vs Croatia
        "sr:sport_event:65606058",  # 2025-11-18 | Jordan vs Mali
        "sr:sport_event:65214520",  # 2025-11-18 | Morocco vs Uganda
        "sr:sport_event:64684832",  # 2025-11-18 | Brazil vs Tunisia
        "sr:sport_event:56418339",  # 2025-11-18 | Kosovo vs Switzerland
        "sr:sport_event:56418341",  # 2025-11-18 | Sweden vs Slovenia
        "sr:sport_event:56418503",  # 2025-11-18 | Scotland vs Denmark
        "sr:sport_event:56418551",  # 2025-11-18 | Spain vs Turkiye
        "sr:sport_event:56418613",  # 2025-11-18 | Austria vs Bosnia and Herzegovina
        "sr:sport_event:56418693",  # 2025-11-18 | Belgium vs Liechtenstein
        "sr:sport_event:65203578",  # 2025-11-18 | Korea Republic vs Ghana
        "sr:sport_event:65202002",  # 2025-11-18 | Japan vs Bolivia
        "sr:sport_event:65200794",  # 2025-11-18 | Saudi Arabia vs Algeria
        "sr:sport_event:65728412",  # 2025-11-18 | Uzbekistan vs IR Iran
        "sr:sport_event:64550266",  # 2025-11-18 | Iraq vs United Arab Emirates
        "sr:sport_event:65577622",  # 2025-11-18 | Kenya vs Senegal
        "sr:sport_event:65204170",  # 2025-11-18 | Oman vs Ivory Coast
        "sr:sport_event:67613698",  # 2026-03-26 | Brazil vs France
        "sr:sport_event:70009604",  # 2026-03-26 | Croatia vs Colombia
        "sr:sport_event:65897794",  # 2026-03-26 | Ukraine vs Sweden
        "sr:sport_event:68020950",  # 2026-03-26 | Qatar vs Serbia
        "sr:sport_event:65897784",  # 2026-03-26 | Wales vs Bosnia and Herzegovina
        "sr:sport_event:69265542",  # 2026-03-27 | Uzbekistan vs Gabon
        "sr:sport_event:68043028",  # 2026-03-27 | New Zealand vs Finland
        "sr:sport_event:68268632",  # 2026-03-27 | China PR vs Curacao
        "sr:sport_event:68042876",  # 2026-03-27 | Chile vs Cape Verde
        "sr:sport_event:68268726",  # 2026-03-27 | Australia vs Cameroon
        "sr:sport_event:68269026",  # 2026-03-29 | Haiti vs Tunisia
        "sr:sport_event:67805524",  # 2026-03-29 | Mexico vs Portugal
        "sr:sport_event:67762770",  # 2026-03-30 | Germany vs Ghana
        "sr:sport_event:69265550",  # 2026-03-30 | Uzbekistan vs Venezuela
        "sr:sport_event:69797936",  # 2026-03-30 | New Zealand vs Chile
        "sr:sport_event:68045106",  # 2026-03-30 | Cape Verde vs Finland
        "sr:sport_event:67763768",  # 2026-03-31 | Norway vs Switzerland
        "sr:sport_event:68020954",  # 2026-03-31 | Serbia vs Saudi Arabia
        "sr:sport_event:68269344",  # 2026-03-31 | Haiti vs Iceland
        "sr:sport_event:68269664",  # 2026-03-31 | Austria vs Korea Republic
        "sr:sport_event:65901002",  # 2026-03-31 | Sweden vs Poland
        "sr:sport_event:69829460",  # 2026-03-31 | South Africa vs Panama
        "sr:sport_event:68913832",  # 2026-03-31 | Morocco vs Paraguay
        "sr:sport_event:69164810",  # 2026-03-31 | Algeria vs Uruguay
        "sr:sport_event:69466342",  # 2026-03-31 | Scotland vs Ivory Coast
        "sr:sport_event:65901000",  # 2026-03-31 | Bosnia and Herzegovina vs Italy
        "sr:sport_event:67763828",  # 2026-03-31 | England vs Japan
        "sr:sport_event:67763830",  # 2026-03-31 | Netherlands vs Ecuador
        "sr:sport_event:69829446",  # 2026-03-31 | Jordan vs Nigeria
        "sr:sport_event:68269258",  # 2026-03-31 | Australia vs Curacao
        "sr:sport_event:66456904",  # 2026-06-11 | Mexico vs South Africa
        "sr:sport_event:71957758",  # 2026-06-11 | Bolivia vs Algeria
        "sr:sport_event:71170506",  # 2026-06-11 | Austria vs Guatemala
        "sr:sport_event:66456940",  # 2026-06-13 | USA vs Paraguay
        "sr:sport_event:66456930",  # 2026-06-14 | Haiti vs Scotland
        "sr:sport_event:66456942",  # 2026-06-14 | Australia vs Turkiye
        "sr:sport_event:66456996",  # 2026-06-15 | Saudi Arabia vs Uruguay
        "sr:sport_event:66456970",  # 2026-06-15 | Sweden vs Tunisia
        "sr:sport_event:66456994",  # 2026-06-15 | Spain vs Cape Verde
        "sr:sport_event:66456982",  # 2026-06-15 | Belgium vs Egypt
        "sr:sport_event:66457008",  # 2026-06-16 | Iraq vs Norway
        "sr:sport_event:66456984",  # 2026-06-16 | IR Iran vs New Zealand
        "sr:sport_event:66457006",  # 2026-06-16 | France vs Senegal
        "sr:sport_event:66457018",  # 2026-06-17 | Argentina vs Algeria
        "sr:sport_event:66457020",  # 2026-06-17 | Austria vs Jordan
        "sr:sport_event:66457030",  # 2026-06-17 | Portugal vs Congo DR
        "sr:sport_event:66457042",  # 2026-06-17 | England vs Croatia
        "sr:sport_event:66457044",  # 2026-06-17 | Ghana vs Panama
        "sr:sport_event:66456920",  # 2026-06-18 | Canada vs Qatar
        "sr:sport_event:66456922",  # 2026-06-18 | Switzerland vs Bosnia and Herzegovina
        "sr:sport_event:66457032",  # 2026-06-18 | Uzbekistan vs Colombia
        "sr:sport_event:66456910",  # 2026-06-18 | Czechia vs South Africa
        "sr:sport_event:66456908",  # 2026-06-19 | Mexico vs Korea Republic
        "sr:sport_event:66456944",  # 2026-06-19 | USA vs Australia
        "sr:sport_event:66456934",  # 2026-06-19 | Scotland vs Morocco
        "sr:sport_event:66456932",  # 2026-06-20 | Brazil vs Haiti
        "sr:sport_event:66456946",  # 2026-06-20 | Turkiye vs Paraguay
        "sr:sport_event:66456974",  # 2026-06-21 | Tunisia vs Japan
        "sr:sport_event:66457076",  # 2026-06-21 | Ecuador vs Curacao
        "sr:sport_event:66457010",  # 2026-06-22 | France vs Iraq
        "sr:sport_event:66457022",  # 2026-06-22 | Argentina vs Austria
        "sr:sport_event:66456988",  # 2026-06-22 | New Zealand vs Egypt
        "sr:sport_event:66457012",  # 2026-06-23 | Norway vs Senegal
        "sr:sport_event:66457024",  # 2026-06-23 | Jordan vs Algeria
        "sr:sport_event:66457034",  # 2026-06-23 | Portugal vs Uzbekistan
        "sr:sport_event:66457046",  # 2026-06-23 | England vs Ghana
        "sr:sport_event:66457048",  # 2026-06-23 | Panama vs Croatia
        "sr:sport_event:66457036",  # 2026-06-24 | Colombia vs Congo DR
        "sr:sport_event:66456924",  # 2026-06-24 | Switzerland vs Canada
        "sr:sport_event:66456926",  # 2026-06-24 | Bosnia and Herzegovina vs Qatar
        "sr:sport_event:66456936",  # 2026-06-24 | Scotland vs Brazil
        "sr:sport_event:66456938",  # 2026-06-24 | Morocco vs Haiti
        "sr:sport_event:66456976",  # 2026-06-25 | Tunisia vs Netherlands
        "sr:sport_event:66457080",  # 2026-06-25 | Curacao vs Ivory Coast
        "sr:sport_event:66456978",  # 2026-06-25 | Japan vs Sweden
        "sr:sport_event:66456914",  # 2026-06-25 | South Africa vs Korea Republic
        "sr:sport_event:66456912",  # 2026-06-25 | Czechia vs Mexico
        "sr:sport_event:66457078",  # 2026-06-25 | Ecuador vs Germany
        "sr:sport_event:66457014",  # 2026-06-26 | Norway vs France
        "sr:sport_event:66457016",  # 2026-06-26 | Senegal vs Iraq
        "sr:sport_event:66456950",  # 2026-06-26 | Paraguay vs Australia
        "sr:sport_event:66457004",  # 2026-06-27 | Cape Verde vs Saudi Arabia
        "sr:sport_event:66456990",  # 2026-06-27 | New Zealand vs Belgium
        "sr:sport_event:66457002",  # 2026-06-27 | Uruguay vs Spain
        "sr:sport_event:66456992",  # 2026-06-27 | Egypt vs IR Iran
]

def get_match_timeline(match_id, retries=0):
    """
    Fetches the timeline of a specific match, with max 3 retries.
    Handles BOTH Rate Limits (429) AND Network Drops (ConnectionError).
    """
    url = f"{BASE_URL}/sport_events/{match_id}/timeline.json"
    headers = {
        "accept": "application/json",
        "x-api-key": API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # THIS IS THE FIX! If the Wi-Fi drops, wait 5 seconds and try again.
        if retries < 3:
            print(f"   ⚠️ Network dropped on {match_id}. Retrying in 5 seconds... (Attempt {retries+1}/3)")
            time.sleep(5)
            return get_match_timeline(match_id, retries + 1)
        else:
            print(f"   ❌ Network failed 3 times on {match_id}. Skipping.")
            return None
    
    # If successful (Status 200), return the data
    if response.status_code == 200:
        return response.json()
    # If we hit the rate limit (Status 429)
    elif response.status_code == 429:
        if retries < 3:
            print(f"   ⚠️ Rate limit hit on {match_id}. Sleeping for 10 seconds... (Attempt {retries+1}/3)")
            time.sleep(10)
            return get_match_timeline(match_id, retries + 1)
        else:
            print(f"   ❌ Rate limit failed 3 times on {match_id}. Skipping.")
            return None
    else:
        print(f"   ❌ Error {response.status_code} on match {match_id}")
        return None

def extract_shots_from_timeline(timeline_data, match_id):
    """
    Parses the Sportradar timeline JSON and pulls out ONLY the shots 
    and their X/Y coordinates, AND maps the real team names!
    """
    shots_data = []
    events = timeline_data.get('timeline', [])
    
    # NEW: Grab the real team names from the match data!
    competitors = timeline_data.get('sport_event', {}).get('competitors', [])
    home_team = competitors[0].get('name', 'Home Team') if len(competitors) > 0 else 'Home Team'
    away_team = competitors[1].get('name', 'Away Team') if len(competitors) > 1 else 'Away Team'
    
    shot_types = ['shot_off_target', 'shot_on_target', 'shot_saved', 'score_change']
    
    for event in events:
        if event.get('type') in shot_types:
            
            # Get the X and Y coordinates
            x = event.get('x')
            y = event.get('y')
            
            # If coordinates exist, save the shot data
            if x is not None and y is not None:
                is_goal = 1 if event.get('type') == 'score_change' else 0
                
                # NEW: Map 'home' or 'away' to the actual country name!
                competitor_str = event.get('competitor', 'home')
                team_name = home_team if competitor_str == 'home' else away_team
                
                shots_data.append({
                    'match_id': match_id,
                    'x': x, 
                    'y': y,
                    'is_goal': is_goal,
                    'team': team_name  # Now this will say "Brazil" instead of "away"!
                })
                
    return pd.DataFrame(shots_data)

# 3. THE MAIN LOOP: This is what actually runs!
if __name__ == "__main__":
    # THE FIX: Use absolute paths so it doesn't matter where your terminal is!
    # This finds the folder where this script lives (src/), goes up one level (..), and into data/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_folder = os.path.join(base_dir, "data")
    
    # Make sure the data folder exists
    os.makedirs(data_folder, exist_ok=True)
    
    all_shots = [] # This list will hold all the shots from all matches
    
    print(f"Starting mass pull of {len(MATCH_IDS)} matches...")
    
    for i, match_id in enumerate(MATCH_IDS):
        print(f"Fetching match {i+1}/{len(MATCH_IDS)} - ID: {match_id}")
        
        # Fetch the data
        timeline = get_match_timeline(match_id)
        
        # Extract the shots
        if timeline:
            shots_df = extract_shots_from_timeline(timeline, match_id)
            if not shots_df.empty:
                all_shots.append(shots_df)
                print(f"   ✅ Found {len(shots_df)} shots!")
            else:
                print("   ⚠️ No shots found in this match.")
        
        # THE COOLDOWN: Sleep for 2.5 seconds to avoid getting banned
        time.sleep(2.5)
        
        # Save progress every 50 matches
        if (i + 1) % 50 == 0 and all_shots:
            temp_df = pd.concat(all_shots, ignore_index=True)
            temp_path = os.path.join(data_folder, "raw_shots_progress.csv")
            temp_df.to_csv(temp_path, index=False)
            print("   💾 Progress saved!")
    
    # FINAL SAVE: Combine all shots into one big CSV file
    if all_shots:
        final_df = pd.concat(all_shots, ignore_index=True)
        final_path = os.path.join(data_folder, "all_qualifier_shots.csv")
        final_df.to_csv(final_path, index=False)
        print(f"\n🎉 SUCCESS! Saved {len(final_df)} total shots to {final_path}")
    else:
        print("\n❌ No shots found. Did you put real Match IDs in the list?")