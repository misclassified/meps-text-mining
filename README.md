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

### Scrape speeches given a list of meps

TODO



