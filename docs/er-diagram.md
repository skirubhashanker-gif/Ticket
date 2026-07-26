# ER Diagram
```mermaid
erDiagram
purchase_headers ||--o{ purchase_line_items : contains
purchase_headers ||--o{ approval_logs : audits
purchase_headers ||--o{ email_queue : queues
users_profile ||--o{ purchase_headers : requests
approval_matrix }o--|| users_profile : approver
```
