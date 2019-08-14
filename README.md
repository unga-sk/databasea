# Tool na development databázy

Zatiaľ podporované a testované DB systémy:
* Postgresql

Zatiaľ podporované a testované OS:
* Linux
* MacOS

## Postup inštalácie
1. Vytvorenie python virtualenv
    ```bash
    $ virtualenv .venv
    $ source .venv/bin/activate
    ```

2. Nainštalovanie python requirements
    ```bash
    $ pip install -r requirements.txt
    ```

3. Inštalácia *pg_dump* (závisí od OS)
4. Inštalácia package
    ```bash
    $ python setup.py install
    ```

## Použitie 
```bash
$ patch-database.py --host 12.3.0.4 --port 5432 --database palshare-refactored --user milan.munko --passwd '' --type upgrade
```