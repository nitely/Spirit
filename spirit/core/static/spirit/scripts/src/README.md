# Installation

## Ubuntu 20.04

### Install Node.js

```
$ sudo apt install gcc g++ make
$ curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
$ sudo apt install -y nodejs
```

> If you are a node.js user then install nvm to manage the versions

### Install yarn (js package manager)

```
$ curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
$ echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
$ sudo apt update && sudo apt install yarn
```

## Fedora 26

### Install Node.js

```
$ sudo dnf install -y gcc-c++ make
$ curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
$ sudo dnf install -y nodejs
```

### Install yarn (js package manager)

```
$ sudo wget https://dl.yarnpkg.com/rpm/yarn.repo -O /etc/yum.repos.d/yarn.repo
$ sudo dnf install -y yarn
```

# Install dependencies

```
$ cd ./Spirit
$ yarn
```

# Build

```
$ make buildjs
```

# Test

```
$ make testjs
```
