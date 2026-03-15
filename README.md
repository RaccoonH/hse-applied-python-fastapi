# hse-applied-python-fastapi
FastAPI project for applied python HSE

## API
1. POST /links/shorten - создает короткую ссылку. 
2. GET /links/{short_code} - перенаправляет на оригинальный URL.
3. DELETE /links/{short_code} - удаляет связь.
4. PUT /links/{short_code} - обновляет короткий URL.
5. GET /links/{short_code}/stats - отображает оригинальный URL, возвращает дату создания, количество переходов, дату последнего использования.
6. POST /links/shorten (с передачей custom_alias) - создание кастомной ссылки.
7. GET /links/search?original_url={url} - поиск ссылки по оригинальному URL.
8. POST /links/shorten  (с параметром expires_at) - создание ссылки с временем жизни.

## Примеры запросов
В качестве коротких кодов для URL используется строка из 8 символов.  
POST /links/shorten, Request body:  
{
  "orig_url": "https://github.com",
  "custom_alias": "12345678",
  "expires_at": "2026-03-09T13:28:08.683Z"
}

GET /links/12345678  

DELETE /links/12345678  

PUT /links/12345678, Request body:  
{
  "custom_alias": "string",
  "expires_at": "2026-03-09T13:29:43.158Z"
}

GET /links/12345678/stats  

GET /links/search?original_url="https://github.com"  


## Запуск
Для запуска необходимо указать нужные перменные окружения, например в .env:
1. DB_FILE - файл базы данных
2. SECRET - секретная строка которая используется для кодирования паролей пользователей
3. REDIS_ADDRESS - адрес redis

Есть два способа запуска:  
1. Docker Compose. Необходимо указать в REDIS_ADDRESS значение redis://redis, далее использовать docker compose up -d
2. One container. Необходимо указать в REDIS_ADDRESS значение redis://localhost:6379, далее использовать Dockerfile


## База данных
Используется две таблицы:
1. User - id, email, hashed_password, is_active, is_superuser, is_verified
2. Link - code, orig_url, creation_time, last_use_time, counter, creator, expires_at


## Тесты
Используются два основных теста:
1. Юнит-тест + интеграционные тесты (pytest). Для из запуска нужно в переменные окружения добавить файл для базы данных: DB_FILE_TEST. После достаточно запустить скрипт run_tests.sh
2. Загрузочные тесты locust, здесь понадобится настроить приложение и запустить его в одном контейнере, и далее запустить locust. Можно воспользоваться скриптом ./run_load_tests.sh

### Текущие результаты тестов
1. Pytest:  
```
Name                      Stmts   Miss  Cover
---------------------------------------------
src/auth/db.py               14      2    86%
src/auth/schemas.py           6      0   100%
src/auth/users.py            26      3    88%
src/config.py                 6      0   100%
src/database.py              12      3    75%
src/links/cache.py           55      7    87%
src/links/database.py        71      2    97%
src/links/models.py          16      2    88%
src/links/router.py         105     10    90%
src/links/schemas.py         10      0   100%
src/links/watcher.py         63      1    98%
src/main.py                  24      6    75%
tests/__init__.py             0      0   100%
tests/conftest.py            90      4    96%
tests/test_auth_api.py       40      0   100%
tests/test_db.py            158      0   100%
tests/test_links_api.py     143      0   100%
tests/test_utils.py          16      1    94%
tests/test_watcher.py        62      0   100%
---------------------------------------------
TOTAL                       917     41    96%
```
2. Locust:
```
Type     Name                                                                                  50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
POST     /auth/jwt/login                                                                       200    280    350    360    410    450    450    460    490    490    490    166
POST     /auth/register                                                                         17     21     24     26     36     88    110    140    150    150    150    110
DELETE   /links/00000000                                                                        10     13     13     35     57     98     98     98     98     98     98     17
GET      /links/00000000                                                                         6      7      8      9      9     48    160    210    210    210    210     64
PUT      /links/00000000                                                                         9     12     13     14     26    110    290    480    480    480    480     61
GET      /links/00000000/stats                                                                   5      6      7      8     12     43     86    100    100    100    100     58
PUT      /links/2OmuH8Cp                                                                        17     17     17     17     17     17     17     17     17     17     17      1
GET      /links/2OmuH8Cp/stats                                                                  11     11     11     11     11     11     11     11     11     11     11      2
PUT      /links/2TR7ryyk                                                                        14     14     14     14     14     14     14     14     14     14     14      1
PUT      /links/2dCneiVT                                                                        14     14     14     14     14     14     14     14     14     14     14      1
PUT      /links/2icogUYE                                                                        19     19     19     19     19     19     19     19     19     19     19      1
GET      /links/2icogUYE/stats                                                                  12     12     12     12     12     12     12     12     12     12     12      1
GET      /links/3YSHh2wu                                                                       580    580    580    610    610    610    610    610    610    610    610      5
GET      /links/3YSHh2wu/stats                                                                   3      3      3      3      3      3      3      3      3      3      3      1
GET      /links/42ydJS56                                                                       590    590    590    590    590    590    590    590    590    590    590      1
PUT      /links/4jLLwMfQ                                                                        25     25     25     25     25     25     25     25     25     25     25      1
GET      /links/5AP6wXjd                                                                       330    330    330    330    330    330    330    330    330    330    330      2
GET      /links/5AP6wXjd/stats                                                                   8      8      8      8      8      8      8      8      8      8      8      1
PUT      /links/64NcQxu6                                                                        13     13     13     13     13     13     13     13     13     13     13      1
GET      /links/6A868qpz                                                                       220    220    220    220    220    220    220    220    220    220    220      1
PUT      /links/6A868qpz                                                                        16     16     16     16     16     16     16     16     16     16     16      1
GET      /links/6GSfxaeD/stats                                                                  10     10     10     10     10     10     10     10     10     10     10      3
GET      /links/7VmxZ5D7                                                                       590    610    640    640    670    670    670    670    670    670    670      7
PUT      /links/7VmxZ5D7                                                                        17     17     17     17     17     17     17     17     17     17     17      1
GET      /links/8etPjyB2                                                                       920    920    920    920    920    920    920    920    920    920    920      2
PUT      /links/8etPjyB2                                                                        17     17     17     17     17     17     17     17     17     17     17      1
GET      /links/8etPjyB2/stats                                                                  13     13     13     13     13     13     13     13     13     13     13      2
GET      /links/9CCJv4B0/stats                                                                  11     11     11     11     11     11     11     11     11     11     11      1
GET      /links/AOIrdsYl                                                                      1000   1000   1000   1000   1000   1000   1000   1000   1000   1000   1000      1
PUT      /links/AOIrdsYl                                                                       470    470    470    470    470    470    470    470    470    470    470      1
DELETE   /links/B4DTSypa                                                                        17     17     17     17     17     17     17     17     17     17     17      1
GET      /links/B4DTSypa                                                                       670    670    670    670    670    670    670    670    670    670    670      1
PUT      /links/BDtexPVL                                                                        16     16     16     16     16     16     16     16     16     16     16      1
GET      /links/BJcsAlxw/stats                                                                   5      5      5      5      5      5      5      5      5      5      5      2
GET      /links/BRQ0ChHx                                                                       590    590    600    600    600    600    600    600    600    600    600      3
GET      /links/BRQ0ChHx/stats                                                                   5      5      8      8      8      8      8      8      8      8      8      3
DELETE   /links/BUIwYEja                                                                        14     14     14     14     14     14     14     14     14     14     14      1
GET      /links/BUIwYEja/stats                                                                   6      6      6      6      6      6      6      6      6      6      6      1
PUT      /links/EDUARTy1                                                                        85     85     85     85     85     85     85     85     85     85     85      1
GET      /links/EfVg9WQx/stats                                                                   9      9     12     12     12     12     12     12     12     12     12      3
GET      /links/FQo4QTLH                                                                       840    840    840    840    840    840    840    840    840    840    840      1
PUT      /links/HaPxWr92                                                                        27     27     27     27     27     27     27     27     27     27     27      1
PUT      /links/HgGLLtjG                                                                        15     15     15     15     15     15     15     15     15     15     15      1
PUT      /links/If38hOMe                                                                        12     12     12     12     12     12     12     12     12     12     12      1
PUT      /links/IjMM4rHS                                                                        21     21     21     21     21     21     21     21     21     21     21      1
GET      /links/IjMM4rHS/stats                                                                   6      6      6      6      6      6      6      6      6      6      6      2
GET      /links/LKlPlRCw/stats                                                                   8      8      8      8      8      8      8      8      8      8      8      1
GET      /links/LYlfuDJ5/stats                                                                   4      4      4      4      4      4      4      4      4      4      4      1
PUT      /links/LamKc9uo                                                                        22     22     22     22     22     22     22     22     22     22     22      1
GET      /links/LamKc9uo/stats                                                                   6      6      6      6      6      6      6      6      6      6      6      1
GET      /links/Lx7rq8is/stats                                                                   9      9      9      9      9      9      9      9      9      9      9      1
PUT      /links/OHSd9in6                                                                        20     20     20     20     20     20     20     20     20     20     20      1
DELETE   /links/QAQ9gCCi                                                                       100    100    100    100    100    100    100    100    100    100    100      1
PUT      /links/Qbhw1en1                                                                        21     21     21     21     21     21     21     21     21     21     21      1
PUT      /links/QmWpFHD1                                                                        14     14     14     14     14     14     14     14     14     14     14      1
PUT      /links/Qp9L78g2                                                                        13     13     13     13     13     13     13     13     13     13     13      1
GET      /links/Qp9L78g2/stats                                                                  11     11     11     11     11     11     11     11     11     11     11      1
GET      /links/QvoWv395                                                                       570    570    590    590    590    590    590    590    590    590    590      3
PUT      /links/Sfr62rQc                                                                        15     15     15     15     15     15     15     15     15     15     15      1
GET      /links/ThYREZC1                                                                       590    620    620    820    820    820    820    820    820    820    820      5
PUT      /links/ThYREZC1                                                                        20     20     20     20     20     20     20     20     20     20     20      1
GET      /links/ThYREZC1/stats                                                                   5      5      5      5      5      5      5      5      5      5      5      3
PUT      /links/WBKMqien                                                                        45     45     45     45     45     45     45     45     45     45     45      1
PUT      /links/WYRttvby                                                                        14     14     14     14     14     14     14     14     14     14     14      1
PUT      /links/XnaHOozZ                                                                        13     13     13     13     13     13     13     13     13     13     13      1
GET      /links/XnaHOozZ/stats                                                                   9      9      9      9      9      9      9      9      9      9      9      1
GET      /links/Y0Ijy0Sf                                                                       220    220    220    220    220    220    220    220    220    220    220      1
PUT      /links/Y0Ijy0Sf                                                                       120    120    120    120    120    120    120    120    120    120    120      1
GET      /links/Y5oTmatX                                                                       590    590    940    940    940    940    940    940    940    940    940      4
GET      /links/Y5oTmatX/stats                                                                  10     10     12     12     12     12     12     12     12     12     12      4
GET      /links/ZKSNRT4G                                                                       580    580    590    590    590    590    590    590    590    590    590      3
PUT      /links/ZKSNRT4G                                                                        23     23     23     23     23     23     23     23     23     23     23      1
GET      /links/ZKSNRT4G/stats                                                                   4      4      4      4      4      4      4      4      4      4      4      1
PUT      /links/Zm579A5d                                                                        14     14     14     14     14     14     14     14     14     14     14      1
GET      /links/b60IYeTD                                                                       930    930    930    930    930    930    930    930    930    930    930      2
PUT      /links/b60IYeTD                                                                        25     25     25     25     25     25     25     25     25     25     25      1
GET      /links/b60IYeTD/stats                                                                   9      9      9      9      9      9      9      9      9      9      9      2
PUT      /links/bm1Z8zHW                                                                        16     16     16     16     16     16     16     16     16     16     16      1
PUT      /links/bymwIyg7                                                                        19     19     19     19     19     19     19     19     19     19     19      1
PUT      /links/dbafmZi2                                                                        19     19     19     19     19     19     19     19     19     19     19      1
GET      /links/e9g2CWkW                                                                       220    220    220    220    220    220    220    220    220    220    220      1
GET      /links/e9g2CWkW/stats                                                                   4      4      4      4      4      4      4      4      4      4      4      1
GET      /links/fAPmNHVm                                                                       220    220    220    220    220    220    220    220    220    220    220      1
PUT      /links/fAPmNHVm                                                                        13     13     13     13     13     13     13     13     13     13     13      1
GET      /links/fZnOzZOs                                                                       590    590    590    590    590    590    590    590    590    590    590      1
PUT      /links/fZnOzZOs                                                                        17     17     17     17     17     17     17     17     17     17     17      1
GET      /links/g6rauuHE                                                                       730    730    730    730    730    730    730    730    730    730    730      2
PUT      /links/g6rauuHE                                                                       280    280    280    280    280    280    280    280    280    280    280      1
PUT      /links/giaGIjKK                                                                        18     18     18     18     18     18     18     18     18     18     18      1
DELETE   /links/hT5Wkxf8                                                                        18     18     18     18     18     18     18     18     18     18     18      1
GET      /links/hT5Wkxf8/stats                                                                   9      9      9      9      9      9      9      9      9      9      9      1
PUT      /links/hjKpQMwI                                                                        11     11     11     11     11     11     11     11     11     11     11      1
GET      /links/iuWUu9Ej/stats                                                                   6      6      6      6      6      6      6      6      6      6      6      1
GET      /links/kDGzvk5h                                                                       720    720    720    720    720    720    720    720    720    720    720      1
DELETE   /links/krJEu0b9                                                                        13     13     13     13     13     13     13     13     13     13     13      1
DELETE   /links/lMLDnapL                                                                        19     19     19     19     19     19     19     19     19     19     19      1
GET      /links/lMLDnapL                                                                       670    670    670    670    670    670    670    670    670    670    670      1
GET      /links/lMLDnapL/stats                                                                  12     12     12     12     12     12     12     12     12     12     12      2
GET      /links/mOLDO9XX                                                                       580    580    580    580    580    580    580    580    580    580    580      1
PUT      /links/mOLDO9XX                                                                        21     21     21     21     21     21     21     21     21     21     21      1
PUT      /links/mnPZg3Am                                                                        19     19     19     19     19     19     19     19     19     19     19      1
GET      /links/mnPZg3Am/stats                                                                  10     10     10     10     10     10     10     10     10     10     10      1
GET      /links/ovX7cd5o                                                                       580    590    590    590    600    600    600    600    600    600    600      7
PUT      /links/ovX7cd5o                                                                        13     13     13     13     13     13     13     13     13     13     13      1
GET      /links/ovX7cd5o/stats                                                                   7      7      7      7      7      7      7      7      7      7      7      3
GET      /links/pBxY3708                                                                       590    590    590    590    590    590    590    590    590    590    590      1
PUT      /links/pBxY3708                                                                        22     22     22     22     22     22     22     22     22     22     22      1
GET      /links/pS4r5tPg                                                                       210    210    590    590    590    590    590    590    590    590    590      3
GET      /links/pS4r5tPg/stats                                                                   7      7      7      7      7      7      7      7      7      7      7      1
GET      /links/pdafqttR                                                                       270    270    270    270    270    270    270    270    270    270    270      2
GET      /links/rDMgTpmy                                                                       680    680    680    680    680    680    680    680    680    680    680      2
PUT      /links/rDMgTpmy                                                                        19     19     19     19     19     19     19     19     19     19     19      1
PUT      /links/rpMwoECG                                                                        21     21     21     21     21     21     21     21     21     21     21      1
PUT      /links/saMj9ic6                                                                        17     17     17     17     17     17     17     17     17     17     17      1
POST     /links/shorten                                                                         24     72    120    130    210    290    350    360    370    370    370    191
GET      /links/t5dz8ZNP                                                                       580    580    580    580    580    580    580    580    580    580    580      1
PUT      /links/t5dz8ZNP                                                                        12     12     12     12     12     12     12     12     12     12     12      1
GET      /links/t5dz8ZNP/stats                                                                   7      7      7      7      7      7      7      7      7      7      7      1
PUT      /links/teCawApK                                                                        24     24     24     24     24     24     24     24     24     24     24      1
GET      /links/uXQsAhoW                                                                       190    190    190    190    190    190    190    190    190    190    190      1
PUT      /links/uXQsAhoW                                                                        17     17     17     17     17     17     17     17     17     17     17      1
PUT      /links/vPPYvzSv                                                                        20     20     20     20     20     20     20     20     20     20     20      1
GET      /links/wM1Oaaff                                                                       210    210    210    210    210    210    210    210    210    210    210      1
GET      /links/wM1Oaaff/stats                                                                   9      9      9      9      9      9      9      9      9      9      9      2
DELETE   /links/wVIfzKQr                                                                        17     17     17     17     17     17     17     17     17     17     17      1
DELETE   /links/wrong_url                                                                       11     11     12     12     13     13     13     13     13     13     13      6
GET      /links/wrong_url                                                                        5      6      6      7      8      9     54     89     89     89     89     63
PUT      /links/wrong_url                                                                        7      8     10     11     18     58     69    270    270    270    270     64
GET      /links/wrong_url/stats                                                                  8     10     11     11     23     40     80    110    110    110    110     62
GET      /links/xprcL7yY                                                                       570    570    570    570    570    570    570    570    570    570    570      2
PUT      /links/xprcL7yY                                                                        15     15     15     15     15     15     15     15     15     15     15      1
GET      /links/xprcL7yY/stats                                                                   7      7      7      7      7      7      7      7      7      7      7      1
PUT      /links/ySNsl1Xe                                                                        12     12     12     12     12     12     12     12     12     12     12      1
DELETE   /links/yUNEjitM                                                                        21     21     21     21     21     21     21     21     21     21     21      1
GET      /links/yUNEjitM                                                                       600    600    630    630    630    630    630    630    630    630    630      3
GET      /links/yUNEjitM/stats                                                                   8      8      8      8      8      8      8      8      8      8      8      3
GET      /links/yyceMNHa                                                                       220    220    220    220    220    220    220    220    220    220    220      1
GET      /links/yyceMNHa/stats                                                                   5      5      5      5      5      5      5      5      5      5      5      1
PUT      /links/zDR4IAZQ                                                                        26     26     26     26     26     26     26     26     26     26     26      1
GET      /links/zpcIwdks                                                                       600    600    600    600    600    600    600    600    600    600    600      1
PUT      /links/zpcIwdks                                                                        82     82     82     82     82     82     82     82     82     82     82      1
GET      /links/zpcIwdks/stats                                                                  18     18     18     18     18     18     18     18     18     18     18      2
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated                                                                             14     42     92    130    340    570    590    670    940   1000   1000   1056
```
