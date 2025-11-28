# 💼 Wallet API — REST API to manage users and wallets

**Wallet API** — This is a REST API service implemented on **FastAPI**, which allows you to:
- Register and authorize users 
- Create wallets and transactions
- Rollback transactions  
- Get analytics on transactions and wallets
- Monitor the system through **Grafana + Prometheus + Loki + Promtail**

## How to run

Create `.env` file in the project root directory and fill it up according to `.envexample` file.

To spin up the whole application, you can enter:

```shell
make up
```

To shut it down, you can enter:

```shell
make down
```

## Explore other available Make commands

To display all available commands and their description, you can enter:

```shell
make help
```

## Test the API using Postman

To test the WalletAPI endpoints using Postman, follow these steps:

1. **Open Postman**
2. **Import the collection**:
   - Click on **File → Import** in Postman.
   - In the Import window, either **drag and drop** the `WalletAPI.postman_collection.json` file or click **Upload Files** and select it.
   - Click **Import**.
3. **Run the requests**: