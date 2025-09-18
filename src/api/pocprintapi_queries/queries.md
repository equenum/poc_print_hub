### Print notification message

```shell
curl \
    -X POST http://127.0.0.1:8000/publish \
    -H "Content-Type: application/json" \
    -d @print-body.json
```

### Get printer status

```shell
curl -X GET http://127.0.0.1:8000/status 
```

### Feed printer paper

```shell
curl \
    -X POST http://127.0.0.1:8000/feed \
    -H "Content-Type: application/json" \
    -d @feed-body.json
```

_(Optional) n_times - number of times to feed (5 <= n_times <= 255); defaults to 5_

### Cut printer paper

```shell
curl -X POST http://127.0.0.1:8000/cut
```
