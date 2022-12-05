# Broadlink Listener


[![pypi](https://img.shields.io/pypi/v/broadlink-listener.svg)](https://pypi.org/project/broadlink-listener/)
[![python](https://img.shields.io/pypi/pyversions/broadlink-listener.svg)](https://pypi.org/project/broadlink-listener/)
[![Build Status](https://github.com/gpongelli/broadlink-listener/actions/workflows/dev.yml/badge.svg)](https://github.com/gpongelli/broadlink-listener/actions/workflows/dev.yml)
[![codecov](https://codecov.io/gh/gpongelli/broadlink-listener/branch/main/graphs/badge.svg)](https://codecov.io/github/gpongelli/broadlink-listener)



Broadlink IR codes listener and SmartIR json generator.

This project will install a `broadlink-listener` command line tool that can be used to generate a climate [SmartIR](https://github.com/smartHomeHub/SmartIR)
compatible json, starting from an initial structure that defines climate behavior, putting Broadlink IR remote to
listening state, until all IR code combination will being scan.


* Documentation: <https://gpongelli.github.io/broadlink-listener>
* GitHub: <https://github.com/gpongelli/broadlink-listener>
* PyPI: <https://pypi.org/project/broadlink-listener/>
* Free software: MIT


## Features

* Discover Broadlink IR remote
* Starting from SmartIR json structure like
```json
{
  "supportedController": "Broadlink",
  "minTemperature": 16,
  "maxTemperature": 31,
  "precision": 1,
  "operationModes": [
    "op_a",
    "op_b"
  ],
  "fanModes": [
    "fan_a",
    "fan_b"
  ],
  "swingModes": [
    "swing_a",
    "swing_b"
  ]
}
```
  it helps you listen all the defined IR codes to create a json like
```json
{
  "supportedController": "Broadlink",
  "minTemperature": 16,
  "maxTemperature": 31,
  "precision": 1,
  "operationModes": [
    "op_a",
    "op_b"
  ],
  "fanModes": [
    "fan_a",
    "fan_b"
  ],
  "swingModes": [
    "swing_a",
    "swing_b"
  ],
  "commands": {
    "off": "...",
    "op_a": {
        "fan_a": {
            "swing_a": {
                "16": "....",

                "31": "...."
            },
            "swing_b": {
                "16": "....",

                "31": "...."
            }
        },
        "fan_b": {
            "swing_a": {
                "16": "....",

                "31": "...."
            },
            "swing_b": {
                "16": "....",

                "31": "...."
            }
        }
    },
    "op_b": {
        "fan_a": {
            "swing_a": {
                "16": "....",

                "31": "...."
            },
            "swing_b": {
                "16": "....",

                "31": "...."
            }
        },
        "fan_b": {
            "swing_a": {
                "16": "....",

                "31": "...."
            },
            "swing_b": {
                "16": "....",

                "31": "...."
            }
        }
    }
  }
}
```

* Mandatory fields into starting json
  * `supportedController`, `minTemperature`, `maxTemperature`, `precision`
* Optional fields (at least one must be present or nothing will be listened):
  * `operationModes`, `fanModes`,`swingModes`
* Generated file can be used into SmartIR HomeAssistant component


## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [gpongelli/cookiecutter-pypackage](https://github.com/gpongelli/cookiecutter-pypackage) project template.
