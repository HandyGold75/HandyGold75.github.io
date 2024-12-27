#!/bin/bash

update(){
    go get go@latest || { echo -e "\033[31mFailed: $1.*\033[0m" ; return 1; }
    go get -u || { echo -e "\033[31mFailed: $1.*\033[0m" ; return 1; }
    go mod tidy || { echo -e "\033[31mFailed: $1.*\033[0m" ; return 1; }
    for indirect in $(tail +3 go.mod | grep "// indirect" | awk '{if ($1 =="require") print $2; else print $1;}'); do go get -u "${indirect}"; done
    go get -u || { echo -e "\033[31mFailed: $1.*\033[0m" ; return 1; }
    go mod tidy || { echo -e "\033[31mFailed: $1.*\033[0m" ; return 1; }
}

buildwasm(){
    ( env GOOS=js GOARCH=wasm go build -o "$1.wasm" . && echo -e "\033[32mBuild: $1.wasm\033[0m" ) || { echo -e "\033[31mFailed: $1.wasm\033[0m" ; return 1; }
}

file="./docs/wasm/main"

update "$file" && buildwasm "$file"
