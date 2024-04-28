#!/bin/bash

GOOS=js GOARCH=wasm go build -o ./docs/wasm/main.wasm

