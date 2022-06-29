# Web Portal
Web-Portal is a web app written in Python using Quart, that aims to provide an easy and fast way to manage the links to all of your web services.

It has been designed to run through docker and it is recommended to put it behind a proxy like Nginx for custom routing and domain names.

## Features
- Minimal use of Javascript, to provide a lightning fast experience
- Icon based UI
- Minimal docker image (if deployed with docker)
- Adjustable site theme
- Plugin support
- Inbuilt widgets
  - Links
    - Groups
    - Colors
    - Icons
  - Search bar
  - HTML embed
  - Website embed (through iframe)
- Password protection for admin modification
- Optionally secure the portal with user accounts & passwords
- MySQL/MariaDB and sqlite support

## Showcase (V1)
[![web-portal showcase image, showing dark and light themes](docs/assets/portal-view.png)](docs/assets/portal-view.png)

## Demo Video (V1)
[![Demo Video](https://img.youtube.com/vi/VIWvmfFK5V0/0.jpg)](https://youtu.be/VIWvmfFK5V0 "Demo Video")

<https://youtu.be/VIWvmfFK5V0>

## About The Repo
- This repo uses 'master' as the develop branch and should be treating unstable or unfinished. If you want a stable release please use the tags/releases.
- The [CHANGELOG](CHANGELOG.md) contains a history of changes that happened with each release.

More details and guides on installing can be found in `docs`, or click [here](docs/index.md).

## License
Copyright (c) 2022 Leo Spratt licenced under AGPL-3, the licence can be found in: `LICENSE.txt`. This project also uses some third-party code, licenses for those can be found at: `THIRD-PARTY.txt`.
