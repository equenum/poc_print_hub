# poc_print_hub

Simple, yet robust selfhosted solution for delivering messages / notifications via a network printer. Intended primary use is, but not limited to, serving as a notification sink for a homelab infrastructure, recieving and printing notifications in the privacy of a local network.

![Solution architecture diagram](assets/solution_architecture_diagram.png)

## poc-print-api

Web-API + Admin page, enables print message publishing / processing, tenant authentication, as well as printer communication via the network and printer functions control (get status, feed paper, cut paper, etc.).

### Endpoints

| Verb | Url | Allowed Tenant Roles | Notes |
|---|---|---|---|
| `POST` | `api/queues/publish` | ADMIN, USER | Publishes messages for printing |
| `POST` | `api/queues/republish` | ADMIN | Republishes all messages from `error` to `print` queue |
| `GET` | `api/queues/status` | ADMIN | Returns `print` and `error` queue statuses: `isOnline`, `count` |
| `GET` | `api/printer/status` | ADMIN | Returns printer status: `name`, `isOnline`, `paperStatus` |
| `POST` | `api/printer/feed` | ADMIN | Feeds printer paper `n_times` |
| `POST` | `api/printer/cut` | ADMIN | Cuts paper (feeds `n*6` times, then cuts) |
| `POST` | `api/tenant/role` | ADMIN, USER | Returns tenant role: `tenantId`, `role` |

Request examples [here](src/api/pocprintapi_queries/queries.md). Make sure to create test tenant entries before using the queries (best done via the `Admin` page, instructions below):

| Tenant Id | Tenant Token | Role |
|---|---|---|
| `admin-test-id` | `admin-test-token` | ADMIN |
| `user-test-id` | `user-test-token` | USER |
