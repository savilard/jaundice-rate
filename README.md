<h1 align="center">Jaundiced news filter</h1>

<p align="center">
  <img alt="Platform" src="https://img.shields.io/badge/platform-linux-green?style=for-the-badge" />
  <img alt="Python version" src="https://img.shields.io/badge/python-3.10-green?style=for-the-badge" />
</p>

---

<!-- TOC -->
  * [Description](#description)
  * [Installation](#installation)
  * [How to run](#how-to-run)
  * [Environment variables](#environment-variables)
  * [How to use](#how-to-use)
  * [For developers](#for-developers)
    * [Install dev deps](#install-dev-deps)
    * [Run flake8](#run-flake8)
    * [Run tests](#run-tests)
<!-- TOC -->

## Description
Microservice for determining the degree of "yellowness" (emotional coloring) of a text.

For now, only one news site is supported - [Inosmi.ru](https://inosmi.ru/). A special adapter has been developed for it that can highlight the text of an article against the rest of the HTML markup. Other news sites will require new adapters, all of which will be located in the adapters directory. The code for Inosmi.ru is also placed there: adapters/inosmi_ru.py.

In the future, it is possible to create a universal adapter suitable for all sites, but its development will be complicated and require additional time and effort.

## Installation

Install using [poetry](https://python-poetry.org/):
```bash
git clone https://github.com/savilard/jaundice-rate.git
cd jaundice-rate
poetry install --without dev
```

## How to run

```shell
poetry run python jaundice_rate/server.py
```

## Environment variables

- `FETCH_TIMEOUT` - The response time, after which the script stops working or moves on to the next link. Default 3 sec.
- `URL_LIMIT` - The number of analyzed links to articles. Default 10.
- `CHARGED_WORDS_DIRECTORY` - charged words directory. Default `jaundice_rate/charged_dict`


## How to use

To start, the service needs to pass a GET request for a list of url containing the texts. Example:

`http://0.0.0.0:8080/?urls=https://inosmi.ru/20230328/indiya-261728000.html,https://inosmi.ru/20230328/kosovo-261727700.html`

After downloading and cleaning the text from the markup, the service performs lemmatization (bringing the word to its normal form). The obtained words are checked to be in the dictionary of emotionally colored words, on the basis of which the text is given a rating. The higher the rating, the more "yellow" the text. The result is returned in json format.

## For developers

### Install dev deps

```shell
poetry install
```

### Run flake8

```shell
poetry run flake8
```

### Run tests

```shell
poetry run pytest
```
