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
