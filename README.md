# ProtonLauncher

ProtonLauncher is a project aimed at simplifying the process of launching and managing non-steam games using [Proton-GE](https://github.com/GloriousEggroll/proton-ge-custom).

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Build](#build)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction
ProtonLauncher is designed to help users easily launch and manage applications with Proton, a compatibility layer for running Windows games on Linux. Using this app, you can create easy shortcuts for your non-Steam games and run them without needing Steam to be open. (It is necessary to install Steam and [Proton-GE](https://github.com/GloriousEggroll/proton-ge-custom) to use this application).

## Features
- Easy game management
- User-friendly interface
- Easy shortcut creation
- Option to set MangoHud
- Search the game on ProtonDB

## Build
1. Clone the repository:
    ```sh
    git clone https://github.com/CesarGarza55/ProtonLauncher.git
    ```
2. Navigate to the project directory:
    ```sh
    cd ProtonLauncher
    ```
3. Build:
    ```sh
    chmod +x compile-linux.sh
    ./compile-linux.sh
    ```

## Usage
To start using ProtonLauncher, run the following command:
```sh
./ProtonLauncher.bin
```
Or install the debian package
```sh
sudo dpkg -i ProtonLauncher.deb
```

## Contributing
Contributions are welcome! Follow these steps to contribute:

- Fork the repository.
- Create a new branch (git checkout -b feature/new-feature).
- Make the necessary changes and commit (git commit -am 'Add new feature').
- Push the changes to your repository (git push origin feature/new-feature).
- Open a Pull Request on GitHub.

## License
This project is licensed under the GNU GPLv2. See the [LICENSE](LICENSE) file for details.