# meps-text-mining

The objective of this project is the analysis of Member of European Parliaments work.

After scraping the parliamentary interventions of MEPS, I'm interested in finding out how
frequent each MP or group give contributions, which topics are more frequent and what 
sentiment is attached to those topics.

The project uses ChatGPT for text analysis.


### Scrape list of meps for a given country

The list of MEPS with ID, political group and national political group can be scraped from the european parliament 
website. There is a list for each country that can be accessed by replacing the curly brackets in the URL below, 
with the relevant country code of interest (IT, ES, DE, etc)

"https://www.europarl.europa.eu/meps/en/download/advanced/xml?name=&countryCode={}"

To fecth the list of MEPS for a specific country and save it into a csv file you can 
simply run the following command:

```
cd src
python scrape_list_of_meps <url> --output <location>

```

For example to fetch the list of italian meps:

```
cd src
python3 scrape_list_of_meps.py "https://www.europarl.europa.eu/meps/en/download/advanced/xml?name=&countryCode=IT" --output 'data/meps_it.csv' 
```

In this code the --ouptut parameter is where you save the output file.


### Scrape speeches given a list of meps

Once you have the list of Meps you can start scraping the speeches from the europarl website. **Note** -> The list of maps is a csv file with the following columns: 

| Column      | Description |
| ----------- | ----------- |
| fullName      | Str: Name of the MP     |
| country   | Str: MP Country        |
| politicalGroup   | Str: Europarl political group        |
| id   | Int: ID required to build the speeches url for every single MP |
| nationalPoliticalGroup   | Str: National Political Group     |

To scrape a new list of MEPS run the following command 

```
cd src
python scrape_meps_speeches.py <meps list location>
```

If you simply want to update a set of already scraped speeches run the following command instead

```
cd src
python scrape_meps_speeches.py <meps list location> --update True
```

Note: the scraping process is deliberately slow, with added sleep time to be respectul of the Europarliamt Website and not cause any harm to users. 