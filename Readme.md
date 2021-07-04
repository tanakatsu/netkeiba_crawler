# Netkeiba crawer

Data crawler for [netkeiba.com](http://www.netkeiba.com)

## Get started

Install dependency package.

```
$ pip install -r requirements.txt
```

Fetch data.

```
$ python3 getdata.py [--max_page num_of_pages] [--output output_filename]
```

#### Data

- id
- name
- sex
- birth_year
- stable
- sire
- mare
- bms
- owner
- breeder
- prize


## Customization

Edit request parameters depending on your needs.

Default parameters are as below.

```
    payload = {
        'pid':'horse_list', 
        'under_age': 2,
        'sort':'prize', 
        'list': self.list_size
    } 
```

