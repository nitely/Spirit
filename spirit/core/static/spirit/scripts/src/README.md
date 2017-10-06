# Installation

## Ubuntu 16.04

### Install Node.js

```
$ curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
$ sudo apt-get install -y nodejs
```

> If you are a node.js user then install nvm to manage the versions

### Install yarn (js package manager)

```
$ curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
$ echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
$ sudo apt-get update && sudo apt-get install yarn
```

> On Ubuntu 17 you may want to remove `cmdtest` if you get any error `sudo apt remove cmdtest`

## Fedora 26

### Install Node.js

```
$ sudo dnf install -y gcc-c++ make
$ curl -sL https://rpm.nodesource.com/setup_6.x | sudo -E bash -
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
$ npm run gulp coffee
```

# Test

```
$ npm run gulp test
```
