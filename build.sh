#!/bin/bash

go mod tidy
go get -u -d ./
GOOS=js GOARCH=wasm go build -o ./docs/wasm/main.wasm  && echo -e "\033[32mBuild: ./docs/wasm/main.wasm\033[0m" || echo -e "\033[31mFailed: ./docs/wasm/main.wasm\033[0m"
