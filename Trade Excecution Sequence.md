# Trade Execution Sequence Diagram (Market Order)

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI Backend
    participant Eng as Matching Engine
    participant DB as Database

    U->>API: Place order (buy/sell, qty, price)
    API->>DB: Validate user balance / holdings
    DB-->>API: OK

    API->>Eng: Submit order
    Eng->>DB: Query opposite order book (Bids/Asks)
    DB-->>Eng: Matching orders found

    Eng->>DB: Create Transaction record
    Eng->>DB: Update matched order status
    Eng->>DB: Update Holdings (buyer +, seller -)
    Eng->>DB: Update balances (buyer -, seller +)

    Eng-->>API: Trade result
    API-->>U: Order confirmation
```

**Flow summary:**
- Validation happens before the order ever reaches the Matching Engine, so bad orders never enter the order book.
- Every state change (Transaction, order status, Holdings, balances) is written by the Matching Engine only — no other component mutates trade-related tables directly.
- The user receives one final confirmation once all downstream updates complete.
