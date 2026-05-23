# API Contract Draft

This skeleton keeps the current C# contract first, then leaves room for a clearer v2 contract.

## Current Compatible Endpoint

Base URL default:

```text
http://localhost:5000/print/
```

### GET `/print/`

Health check.

Response:

```text
Welcome
```

### POST `/print/`

Compatible request body:

```json
[
  {
    "kit": "LOAI BO",
    "sku": "",
    "qty": ""
  },
  {
    "kit": "K123456",
    "sku": "12345678",
    "qty": "4321"
  }
]
```

Success response:

```json
{
  "success": true,
  "message": "Print job accepted"
}
```

Validation error response:

```json
{
  "success": false,
  "message": "Missing required field: sku"
}
```

## Future Request Shape

Preferred v2 body:

```json
{
  "labels": [
    {
      "kit": "LOAI BO",
      "sku": "",
      "qty": ""
    }
  ]
}
```
