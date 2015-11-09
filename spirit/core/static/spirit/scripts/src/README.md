## Installation (Ubuntu 14.04)

Install io.js
```
$ curl -sL https://deb.nodesource.com/setup_iojs_3.x | sudo -E bash -
$ sudo apt-get install -y iojs
```

Install dependencies
```
$ cd ./Spirit
$ npm install -y .
```

## Build

```
$ npm run gulp coffee
```

## Test

```
$ npm run gulp test
```
