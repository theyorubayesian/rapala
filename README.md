# Rapala

This project, `Rapala` is a VOA News Scraper that combines multiprocessing and multithreading to collect news articles from VOA News Websites. 

`Rapala` is a Yoruba word that is close to `welter` (to move in a turbulent fashion) in meaning. In Yoruba pop culture, the term `Omo rapala` was popularised by Fuji musician, [Akande Abass Obesere](https://en.wikipedia.org/wiki/Obesere), in his popularly acclaimed albums, `Asakasa` and `O.B.T.K.` where he proclaimed himself `Omo Rapala Commander`. [Niniola](https://en.wikipedia.org/wiki/Niniola) reintroduced the term in her Sarz-assisted record, `Omo Rapala`, an ode to female appeal and guile.

| Languages / Countries | Language Code | Website |
| --------- | ------------- | ------- |
| Afaan oromoo | orm | https://www.voaafaanoromoo.com/ |
| Afrique | afr | https://www.voaafrique.com/ |
| Amharic | amh | https://amharic.voanews.com/ |
| Bambara | bam | http://www.voabambara.com/ |
| Hausa | hau | https://www.voahausa.com/ |
| Kinyarwanda | kin | https://www.radiyoyacuvoa.com/ |
| Ndebele | nde | https://www.voandebele.com/ |
| Somali | som | https://www.voasomali.com/ |
| Swahili | swa | https://www.voaswahili.com/ |
| Tigrinya | tir | https://tigrigna.voanews.com/ |
<!-- | Lingala | lin | https://www.voalingala.com/ | -->
<!-- | Shona | sna | www.voashona.com | -->
<!-- | Zimbabwe | zim | https://www.voazimbabwe.com/ | -->

This scraper works fine as of `25th of December, 2022`.

## Setup & Installation
- Create a virtual environment 
-  Install required packages
```
pip install -r requirements.txt
```

## Using the scraper
- To scrape all articles from all categories
```
python -m rapala --language <language-code> --output_file_name=<filename.tsv> --categories=all --cleanup
```
- To scrape a finite amount of articles from all categories
```
python -m rapala --no_of_articles=<no-of-articles> --language <language-code> --output_file_name=<filename.tsv> --categories=all --cleanup --spread
```
- To check the full list of arguments for the scraper
```
python -m rapala --help
```

You can check language codes in the table above.
The scraper output should be a `tsv` file with four columns: `heading`, `content`, `category`, `url`. See sample output in [data](data/)

## Contribution
VOA may change the HTML class attributes and structure of its websites. To ensure that this scraper is maintainable over time, class attributes and other such configurations are separated into [config.yml](config.yml) and [constants.py](src/constants.py).

Feel free to raise an issue & open a pull request if you discover a bug or want to propose an improvement.
