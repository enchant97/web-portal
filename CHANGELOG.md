# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0] - 2022-06-04
### Added
- Run the app with HTTPS through docker
### Changed
- Update pip requirements

## [1.5.0] - 2022-04-23
### Added
- Group deletion
- Unit tests
- New config for controlling whether to open links in new tab
### Changed
- Improve link color
- Update pip requirements
- Update theme-changer.js to V1
- Theme changer is now a large popup
- Optimise css theme variables
- Placeholder for input elements
- Improve nav, heading and mobile styling
### Removed
- Custom scrollbar in favour for css "color-scheme"

## [1.4.0] - 2022-03-12
### Added
- Export widgets into JSON
- Import widgets from JSON
### Changed
- Split admin page into multiple pages (there was a lot of settings)

## [1.3.0] - 2022-03-06
### Added
- Compact mode
- Admin reset
### Changed
- Update pip requirements
- Improve docker image
- Move web_portal out of src
- Style improvements
### Fixed
- Panel headers not showing
### Removed
- Removed running development server (`__main__.py` file)

## [1.2.0] - 2021-11-14
### Added
- Add theme changer
- Add search box
### Changed
- Alter way app is run
- Make panel widgets more aligned
- Update pip requirements
- Create a compact docker image
- Style improvements & use icons for buttons

## [1.1.1] - 2021-07-13
### Changed
- Just a pip requirements update
- Default support for MySQL.

## [1.1.0] - 2021-05-20
### Changed
- Order widgets by prefix
- Allow for widget URL to be modified
- Update pip requirements
### Removed
- Remove BASE_URL config

## [1.0.1] - 2021-03-28
### Fixed
- Update docker files
- Minor bug fix

## [1.0.0] - 2021-02-11
### Added
- First stable & public version
