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

# Panic when importing net/http using go 1.24.0, go 1.23.0 does seem to work properly
#
# panic: syscall/js: call of Value.Int on undefined wasm_exec.js:22:14
# <empty string> wasm_exec.js:22:14
# goroutine 1 [running]: wasm_exec.js:22:14
# syscall/js.Value.float({{}, 0x0, 0x0}, {0x6df82, 0x9}) wasm_exec.js:22:14
# 	/home/handygold75/go/pkg/mod/golang.org/toolchain@v0.0.1-go1.24.0.linux-amd64/src/syscall/js/js.go:523 +0x10 wasm_exec.js:22:14
# syscall/js.Value.Int(...) wasm_exec.js:22:14
# 	/home/handygold75/go/pkg/mod/golang.org/toolchain@v0.0.1-go1.24.0.linux-amd64/src/syscall/js/js.go:540 wasm_exec.js:22:14
# syscall.init() wasm_exec.js:22:14
# 	/home/handygold75/go/pkg/mod/golang.org/toolchain@v0.0.1-go1.24.0.linux-amd64/src/syscall/fs_js.go:32 +0x37
