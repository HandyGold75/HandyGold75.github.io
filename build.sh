#!/bin/bash

go mod edit -go "$(go version | { read -r _ _ v _; echo "${v#go}"; })"
go mod tidy
go get -u ./

file="./docs/wasm/main"

env GOOS=js GOARCH=wasm go build -o "$file.wasm" . && echo -e "\033[32mBuild: $file.wasm\033[0m" || echo -e "\033[31mFailed: $file.wasm\033[0m"

