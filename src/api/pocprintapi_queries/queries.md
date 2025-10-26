### Publish notification message

#### Admin

```shell
curl \
    -X POST http://127.0.0.1:8000/publish \
    -H "Content-Type: application/json" \
    -H "PPH-Tenant-Id: admin-test-id" \
    -H "PPH-Tenant-Token: admin-test-token" \
    -d @print-body.json
```

#### Non-Admin

```shell
curl \
    -X POST http://127.0.0.1:8000/publish \
    -H "Content-Type: application/json" \
    -H "PPH-Tenant-Id: user-test-id" \
    -H "PPH-Tenant-Token: user-test-token" \
    -d @print-body.json
```


### Get printer status

#### Admin

```shell
curl \
    -X GET http://127.0.0.1:8000/status \
    -H "PPH-Tenant-Id: admin-test-id" \
    -H "PPH-Tenant-Token: admin-test-token"
```

#### Non-Admin

```shell
curl \
    -X GET http://127.0.0.1:8000/status \
    -H "PPH-Tenant-Id: user-test-id" \
    -H "PPH-Tenant-Token: user-test-token"
```


### Feed printer paper

#### Admin

```shell
curl \
    -X POST http://127.0.0.1:8000/feed \
    -H "Content-Type: application/json" \
    -H "PPH-Tenant-Id: admin-test-id" \
    -H "PPH-Tenant-Token: admin-test-token" \
    -d @feed-body.json
```

#### Non-Admin

```shell
curl \
    -X POST http://127.0.0.1:8000/feed \
    -H "Content-Type: application/json" \
    -H "PPH-Tenant-Id: user-test-id" \
    -H "PPH-Tenant-Token: user-test-token" \
    -d @feed-body.json
```

_(Optional) n_times - number of times to feed (5 <= n_times <= 255); defaults to 5_


### Cut printer paper

#### Admin

```shell
curl \
    -X POST http://127.0.0.1:8000/cut \
    -H "PPH-Tenant-Id: admin-test-id" \
    -H "PPH-Tenant-Token: admin-test-token" \
```

#### Non-Admin

```shell
curl \
    -X POST http://127.0.0.1:8000/cut \
    -H "PPH-Tenant-Id: user-test-id" \
    -H "PPH-Tenant-Token: user-test-token"
```


### Republish all error queue messages

#### Admin

```shell
curl \
    -X POST http://127.0.0.1:8000/republish \
    -H "PPH-Tenant-Id: admin-test-id" \
    -H "PPH-Tenant-Token: admin-test-token" \
```

#### Non-Admin

```shell
curl \
    -X POST http://127.0.0.1:8000/republish \
    -H "PPH-Tenant-Id: user-test-id" \
    -H "PPH-Tenant-Token: user-test-token"
```
