# API curl examples

Default endpoint:

```text
http://localhost:5000/print/
```

The app prints with the schema currently selected in the Settings screen. Select
`canon_schema.json` or `assy_schema.json` before sending a request.

## Health check

Windows PowerShell:

```powershell
curl.exe "http://localhost:5000/print/"
```

Ubuntu/Linux:

```bash
curl "http://localhost:5000/print/"
```

## Print one Canon label

Select `src/assets/template/canon/canon_schema.json` in the app first.

Windows PowerShell:

```powershell
curl.exe -X POST "http://localhost:5000/print/" `
  -H "Content-Type: application/json" `
  --data-binary "@docs\api_samples\canon_request.json"
```

If the terminal is already in the `docs` directory:

```powershell
curl.exe -X POST "http://localhost:5000/print/" `
  -H "Content-Type: application/json" `
  --data-binary "@api_samples\canon_request.json"
```

Ubuntu/Linux:

```bash
curl -X POST 'http://localhost:5000/print/' \
  -H 'Content-Type: application/json' \
  --data-binary '@docs/api_samples/canon_request.json'
```

## Print one Assy label

Select `src/assets/template/assy/assy_schema.json` in the app first.

Windows PowerShell:

```powershell
curl.exe -X POST "http://localhost:5000/print/" `
  -H "Content-Type: application/json" `
  --data-binary "@docs\api_samples\assy_request.json"
```

If the terminal is already in the `docs` directory:

```powershell
curl.exe -X POST "http://localhost:5000/print/" `
  -H "Content-Type: application/json" `
  --data-binary "@api_samples\assy_request.json"
```

Ubuntu/Linux:

```bash
curl -X POST 'http://localhost:5000/print/' \
  -H 'Content-Type: application/json' \
  --data-binary '@docs/api_samples/assy_request.json'
```

## Print multiple labels

Windows PowerShell:

```powershell
curl.exe -X POST "http://localhost:5000/print/" `
  -H "Content-Type: application/json" `
  --data-binary "@docs\api_samples\multiple_labels_request.json"
```

If the terminal is already in the `docs` directory:

```powershell
curl.exe -X POST "http://localhost:5000/print/" `
  -H "Content-Type: application/json" `
  --data-binary "@api_samples\multiple_labels_request.json"
```

Ubuntu/Linux:

```bash
curl -X POST 'http://localhost:5000/print/' \
  -H 'Content-Type: application/json' \
  --data-binary '@docs/api_samples/multiple_labels_request.json'
```

## Wrapped request body

The API also accepts this shape:

```json
{
  "labels": [
    {
      "mold_no": "278-H21-00",
      "parts_no": "RU1-0404"
    }
  ]
}
```

## Expected response

Accepted request:

```json
{
  "success": true,
  "message": "Da nhan lenh in"
}
```

Invalid request:

```json
{
  "success": false,
  "message": "Request body phai co it nhat mot tem."
}
```

Paths beginning with `@docs/...` assume the terminal is in the
`printer_pyside6_qml` project directory. When the terminal is already in
`printer_pyside6_qml/docs`, use `@api_samples/...` instead.
