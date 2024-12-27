#!/bin/bash

update(){
    go mod edit -go "$(go version | { read -r _ _ v _; echo "${v#go}"; })" || { echo -e "\033[31mFailed: $1.*\033[0m" ; return 1; }
    go mod tidy || { echo -e "\033[31mFailed: $1.*\033[0m" ; return 1; }
    go get -u ./ || { echo -e "\033[31mFailed: $1.*\033[0m" ; return 1; }
}

buildwasm(){
    ( env GOOS=js GOARCH=wasm go build -o "$1.wasm" . && echo -e "\033[32mBuild: $1.wasm\033[0m" ) || { echo -e "\033[31mFailed: $1.wasm\033[0m" ; return 1; }
}

file="./docs/wasm/main"

update "$file" && buildwasm "$file"
