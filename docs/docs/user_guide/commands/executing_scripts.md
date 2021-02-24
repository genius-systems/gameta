# Executing Scripts

This section describes Gameta Scripts' feature, it is broken down into several
parts:

1. Introducing Gameta Scripts
2. Using Gameta Scripts

## Introducing Gameta Scripts

Gameta Scripts is a language agnostic script executor, allowing users to draft
scripts in their preferred languages and use Gameta to execute them. Scripting
languages natively supported by Gameta include shell and Python. Additional 
languages are supported but users need to configure these by themselves, see 
the [Adding Scripting Languages] page for more details.

## Using Gameta Scripts

Gameta Scripts are added during the registration procedure. They are stored 
under the `.gameta/scripts` folder, in folders corresponding to the registered
category and prefixes for each language e.g. `*.sh` for shell and `*.py` for 
Python.

Supposing one has a Python script generates an encrypted RSA public and private 
key-pair:

```python
#!/usr/bin/env python3

# Example is adapted from [here]

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def utf8(s: bytes):
    return str(s, 'utf-8')


private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
    backend=default_backend()
)
public_key = private_key.public_key()


private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

with open('private_key.pem', 'wb') as f:
    f.write(private_pem)

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
with open('public_key.pem', 'wb') as f:
    f.write(public_pem)


with open("private_key.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )

with open("public_key.pem", "rb") as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )

```

To utilise this script as a Gameta script, we must first register it:

```shell
# Register the script
gameta scripts register \
  -n generate_rsa_keys \              # Name of the script
  -c linux.encryption  \              # Category of the script
  -d "Generates RSA keys on Linux" \  # A brief description of the script
  -l python \                         # Language that the script is written in
  -p current/path/to/script \         # Relative path where the script is stored
  -e venv=test                        # Optional execution environment key-value parameters, 
                                      # specifies a Python virtualenv called test
```

This will create a copy of the script in the `.gameta` folder under the scripts
folder:

```
.gameta
|--> .gameta  # File for storing Gameta configuration
|--> scripts  # Folder for storing Gameta scripts
     |--> linux
          |--> build
               |--> build_script.sh
|--> configs  # Folder for storing user-defined configurations
```

---
**Note**

If a script is not detected in the specified path, a boilerplate template is
created in the `.gameta/scripts` folder. Users provide the boilerplate template
when they register a new language, see the [Adding Scripting Languages] page for
more details.
---

[Adding Scripting Languages]: ../customisation/adding_scripting_languages.md
[here]: https://gist.github.com/gabrielfalcao/de82a468e62e73805c59af620904c124