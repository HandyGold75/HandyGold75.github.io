FILE := HG75.bin
TARGET := ..

get:
	go get go@latest
	go get -u
	go mod tidy
	for indirect in $(tail +3 go.mod | grep "// indirect" | awk '{if ($1 =="require") print $2; else print $1;}'); do go get -u "${indirect}"; done
	go get -u
	go mod tidy

	cd ./server/src ; \
	go get go@latest ; \
	go get -u ; \
	go mod tidy ; \
	for indirect in $(tail +3 go.mod | grep "// indirect" | awk '{if ($1 =="require") print $2; else print $1;}'); do go get -u "${indirect}"; done ; \
	go get -u ; \
	go mod tidy

build:
	cd ./server/src ; \
	go build -o "$(TARGET)/$(FILE)" .

wasm:
	env GOOS=js GOARCH=wasm go build -o ./docs/wasm/main.wasm .

run:
	cd ./server/src ; \
	go build -o "$(TARGET)/$(FILE)" . && exec "$(TARGET)/$(FILE)"

clean:
	cd ./server/src ; \
	rm -f "$(TARGET)/$(FILE)" ; \
	rm -fr "$(TARGET)/data" ; \
	rm -f "$(TARGET)/config.json"
