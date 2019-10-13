import firebase_admin
from firebase_admin import credentials, firestore


def get_firestore_instance():
    cred = credentials.Certificate(_get_service_credential())
    firebase_admin.initialize_app(cred)
    return firestore.client()


def _get_service_credential():
    return {
        "type": "service_account",
        "project_id": "yotime-2019",
        "private_key_id": "f569e76cd76f0b3962c618a563de2960ff8df9a2",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCth+zy30WtKJ8z\nX0bUq+fGf19MqE0proTb6jvFUEl7rsVIJ3DBOWCrBUfQETL5kbMw5am9wKes2FJc\nfcIemiQUeRh6kXicxQobBuIazQyI1/WW5j95iw9TGi7VMkbvptINE8g9YUVRgd8I\n8vxMS1iP/FmwIYU+y21YEPbcoSGz/b3Ce78OXxtzIxkOuVV2iA2F6QhpnEO2s6FH\njXi/QmYNeClTC0XkFfN8dY4skrkpWF/yD32tgwtTzgEAtwsdTuR82opqtMz5yizB\nR84UI1Hc58CPdmfdmqi7mdIBHKbqb9AWz5+jGK0h3L5N2+8K7wHsXr/QgjqtaCva\nt7sNTaAbAgMBAAECggEAUxl8hvIU089YLam6qa2I2K22XWdbTFKenRGWfe7swaX4\nI41/mYh4mm107lbOKmVzgj75Aj14DnWpO1Gd3DnEfWlgJ5HySGCzbi3lqR/4mK+S\nlCi+zN2jARDQzJe/EJS6kjie84XZRCcFP6vc1kxepNUbvhTPUjroqfu1vAINubtH\nLHQ6YVfYWEUHQOf96xl+q0yQcODWGKSLaWw2kED4qg4mYI+ax4qjKh+sLbea7OPO\nXo1VSyS4186DYWYpzci1GINgLxZeyaDwRi7XLeYCPmRsoommzAka3EmsV5R50KyX\nNzgNPqVpydfjwIqyK6roxie+SJRv71S7lQG+FQDqAQKBgQDe8YOlJK5285XQGOev\nomSHcbtoUsOyoocMCaOGy+nDHsua4mjs6ea5bITMlwqcoV2S+ocNRj97rVbYZSlF\nKKIvROr/VxRhFAtOLrShUd3eg4Mit7NBazYNNwCElSXiboxKAIU04IyzS13si3dq\nMIJ4OeL56NwlKUzCC2AEezIkYQKBgQDHQtA9PHthN9tV1SG6CGnrtXcSw+UasSiz\nJVC5RZKkRyvNbDaVFc8VFqOBuDeUgCjHmMAzpV8RFOJZOWVagwsLeiq5lZBBWbVC\n4OO49KwIOleKZ6qJp7VF7FG2FRnt4S3qrlf0Mzj3bfD42CK39k/rYIR7LxUD7m/E\nC4fY1ygV+wKBgHM5wCCKZOF14+g59wT/mZWnYoT4wcyB0+qU0L/KhHckY3cZrcFE\n4srTG4/iQMnTXNmqQkLKG+WAIXKWVk44QhrMM+jkyNOj2HQAD7uQ5Gss7Yn0B+G3\n16fc1ZewvnPZTwiwXCiIJjBEs7aeHonzqHsa8ATaJW3PeqyP1IB8a94BAoGANDBm\ntDM8KXlkxDVfcQc1HtxXhJ20Suptu4Yhf3UedFKDwXj/Tsr4gxB74MTsIcPzaluy\ns5QzsxiiNDZZOnyqDuZ/fD4VG1iwpgSbAF1tFXaaaRC/1PANBXRg7mzWbryUtyvU\ns4wa9otgGv0ZEs+7nO2ZpV3uhioUMefHO98Wi7MCgYEAlK0LSbtPUjKJAAp/2fsV\nr/KDyBqkdu5ROBQ4+cymvxn/7k7pm+mD7MPXJSKufVJiKlhOzG+8h9Fd7jTd7/Am\nCK3JncxBxEfbNLMOyXr1PQDa92GNgGYa6CiA0yZv7dH3sIlsV4OPSqV4AzxYcOqT\noadOA2rsR+NHUJdhSWTSHQo=\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-ajwpm@yotime-2019.iam.gserviceaccount.com",
        "client_id": "113524746831213317356",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-ajwpm%40yotime-2019.iam.gserviceaccount.com"
    }
