## settings.json
Add `settings.json` on root.

```json
{
  "profiles": [
    {
      "company_code": "test",
      "company_name": "Company Testing"
    }
  ]
}
```

## LetsGO.exe
x86 build only

## Python version
Client is using Python 3.7.2.

## service-account.json
Add `service-account.json` on root (/src).

To create a new `service-account.json`, visit https://console.cloud.google.com/iam-admin/serviceaccounts/details/108078427194927849620;edit=true?project=letsgo-2019
Just add a new key and obtain the `service-account.json`.

