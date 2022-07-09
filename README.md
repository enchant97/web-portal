# Web Portal
Web-Portal is a web app written in Python using Quart, that aims to provide an easy and fast way to manage the links to all of your web services.

It has been designed to run through docker and it is recommended to put it behind a proxy like Nginx for custom routing and domain names.

If you want just a basic link panel configured with a yaml file checkout Web Portal Lite available here: <https://github.com/enchant97/web-portal-lite>.

## Features
- Minimal use of Javascript, to provide a lightning fast experience
- Icon based UI
- Minimal docker image (if deployed with docker)
- Adjustable site theme
- Plugin support
- Inbuilt widgets
  - Digital Clock
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
This project is Copyright (c) 2022 Leo Spratt, licences shown below:

Code

    AGPL-3 or any later version. Full license found in `LICENSE.txt`

Documentation

    FDLv1.3 or any later version. Full license found in `docs/LICENSE.txt`

This project also uses some third party content, licences for those are found at: `THIRD-PARTY.txt`.
