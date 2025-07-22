package Com

import (
	"HG75/lib/DataBase"
	"HG75/modules/Auth"
	"encoding/json"
	"errors"
	"net/http"
	"slices"
	"strconv"
	"time"
)

var (
	openDataBases = map[string]*DataBase.DataBase{}

	dbHelpArgs = "\r\n" +
		"  header [sheet?]\r\n    Get database header.\r\n" +
		"  read [sheet?] [record?]\r\n    Get database or sheet data.\r\n" +
		"  add [sheet] [values,...]\r\n    Add record to sheet.\r\n" +
		"  delete [sheet] [record]\r\n    Delete record from sheet.\r\n" +
		"  move [sheet] [record1] [record2]\r\n    Move record in sheet.\r\n" +
		"  swap [sheet] [record1] [record2]\r\n    Swap 2 records in sheet.\r\n" +
		"  write [sheet] [record] [values,...]\r\n    Overwrite record in sheet.\r\n" +
		"  modify [sheet] [record] [key] [value]\r\n    Overwrite record in sheet.\r\n"

	DateBasesComs = Commands{
		"db-test": Command{
			RequiredAuthLevel:   Auth.AuthMap["user"],
			RequiredRoles:       []string{},
			Description:         "Testing DataBase.",
			DetailedDescription: "Interact with testing DataBase. Usage: db-test [header|read|add|delete|move|swap|write|modify] [args?]..." + dbHelpArgs,
			ExampleDescription:  "read",
			AutoComplete:        []string{"header", "read", "add", "delete", "move", "swap", "write", "modify"},
			ArgsLen:             [2]int{1, 5},
			Function: func(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
				if _, ok := openDataBases[user.Username+"/TestDB"]; !ok {
					err := openDB("TestDB", user, DataBase.Template{
						"Sheet1": []string{"Col1"},
						"Sheet2": []string{"Col1", "Col2"},
						"Sheet3": []string{"Col1", "Col2", "Col3"},
						"Sheet4": []string{"Col1", "Col2", "Col3", "Col4"},
					})
					if err != nil {
						return []byte{}, "", http.StatusInternalServerError, err
					}
				}
				return DBInterface(openDataBases[user.Username+"/TestDB"], "db-test", user, args...)
			},
		},
		"db-asset": Command{
			RequiredAuthLevel:   Auth.AuthMap["user"],
			RequiredRoles:       []string{},
			Description:         "Testing DataBase.",
			DetailedDescription: "Interact with testing DataBase. Usage: db-test [header|read|add|delete|move|swap|write|modify] [args?]..." + dbHelpArgs,
			ExampleDescription:  "read",
			AutoComplete:        []string{"header", "read", "add", "delete", "move", "swap", "write", "modify"},
			ArgsLen:             [2]int{1, 5},
			Function: func(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
				if _, ok := openDataBases[user.Username+"/AssetDB"]; !ok {
					err := openDB("AssetDB", user, DataBase.Template{
						"Devices": []string{"Name", "Brand", "Device", "Series", "S/N", "MAC-WiFi", "MAC-Eth", "DOP", "EOL", "Modified", "Notes"},
						"Assets":  []string{"Name", "Brand", "Asset", "Series", "S/N", "DOP", "EOL", "Modified", "Notes"},
						"Servers": []string{"Name", "Brand", "Server", "Series", "S/N", "MAC", "DOP", "EOL", "Modified", "Notes"},
						"Parts":   []string{"Name", "Brand", "Part", "Series", "S/N", "DOP", "EOL", "Modified", "Notes"},
					})
					if err != nil {
						return []byte{}, "", http.StatusInternalServerError, err
					}
				}
				return DBInterface(openDataBases[user.Username+"/AssetDB"], "db-asset", user, args...)
			},
		},
		"db-license": Command{
			RequiredAuthLevel:   Auth.AuthMap["user"],
			RequiredRoles:       []string{},
			Description:         "License DataBase.",
			DetailedDescription: "Interact with license DataBase. Usage: db-license [header|read|add|delete|move|swap|write|modify] [args?]..." + dbHelpArgs,
			ExampleDescription:  "read",
			AutoComplete:        []string{"header", "read", "add", "delete", "move", "swap", "write", "modify"},
			ArgsLen:             [2]int{1, 5},
			Function: func(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
				if _, ok := openDataBases[user.Username+"/LicenseDB"]; !ok {
					err := openDB("LicenseDB", user, DataBase.Template{
						"Licenses": []string{"Name", "Product", "Key", "URL", "DOP", "EOL", "Cost", "Auto Renew", "Modified", "Notes"},
					})
					if err != nil {
						return []byte{}, "", http.StatusInternalServerError, err
					}
				}
				return DBInterface(openDataBases[user.Username+"/LicenseDB"], "db-license", user, args...)
			},
		},
		"db-query": Command{
			RequiredAuthLevel:   Auth.AuthMap["user"],
			RequiredRoles:       []string{},
			Description:         "Query DataBase.",
			DetailedDescription: "Interact with query DataBase. Usage: db-query [header|read|add|delete|move|swap|write|modify] [args?]..." + dbHelpArgs,
			ExampleDescription:  "read",
			AutoComplete:        []string{"header", "read", "add", "delete", "move", "swap", "write", "modify"},
			ArgsLen:             [2]int{1, 5},
			Function: func(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
				if _, ok := openDataBases[user.Username+"/QueryDB"]; !ok {
					err := openDB("QueryDB", user, DataBase.Template{
						"Links":   []string{"Img", "Text", "Url", "Cat", "Modified"},
						"Contact": []string{"Img", "Text", "Url", "Modified"},
					})
					if err != nil {
						return []byte{}, "", http.StatusInternalServerError, err
					}
				}
				return DBInterface(openDataBases[user.Username+"/QueryDB"], "db-query", user, args...)
			},
		},
	}
)

func openDB(name string, user Auth.User, template DataBase.Template) error {
	db, err := DataBase.New(name, files.DBDir+"/"+user.Username, template)
	if err != nil {
		return errors.New("failed creating or loading database")
	}

	for _, err := range db.Load() {
		lgr.Log("error", user.Username, name, err)
	}

	openDataBases[user.Username+"/"+name] = db

	time.AfterFunc(time.Until(time.Now().Add(time.Minute*time.Duration(30))), func() {
		for _, err := range openDataBases[user.Username+"/"+name].Dump() {
			lgr.Log("error", user.Username, name, err)
		}

		delete(openDataBases, user.Username+"/"+name)
	})

	return nil
}

func DBInterface(db *DataBase.DataBase, com string, user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
	if len(args) < 1 {
		return []byte{}, "", http.StatusBadRequest, errors.New(com + " requires at least 1 arguments")
	}

	switch args[0] {
	case "header":
		if len(args) > 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New(com + " requires requires 0 or 1 argument")
		}

		template := db.GetTemplate()

		if len(args) > 1 {
			templateShort, ok := template[args[1]]
			if !ok {
				return []byte{}, "", http.StatusBadRequest, errors.New("header not found")
			}

			jsonBytes, err := json.Marshal(templateShort)
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}
			return jsonBytes, "application/json", http.StatusOK, nil
		}

		jsonBytes, err := json.Marshal(template)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		return jsonBytes, "application/json", http.StatusOK, nil

	case "read":
		if len(args) == 1 {
			jsonBytes, err := json.Marshal(db.Read())
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return jsonBytes, "application/json", http.StatusOK, nil
		}

		if len(args) > 3 {
			return []byte{}, "", http.StatusBadRequest, errors.New(com + " read requires 0, 1 or 2 arguments")
		}

		sheet, err := db.Open(args[1])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		if len(args) == 2 {
			jsonBytes, err := json.Marshal(sheet.Read())
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return jsonBytes, "application/json", http.StatusOK, nil
		}

		index, err := strconv.Atoi(args[2])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		record, err := sheet.Open(index)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(record.Read())
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "add":
		if len(args) < 3 {
			return []byte{}, "", http.StatusBadRequest, errors.New(com + " add requires at least 2 arguments")
		}

		sheet, err := db.Open(args[1])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		if err := sheet.Add(args[2:]); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(sheet.Read())
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "delete":
		if len(args) != 3 {
			return []byte{}, "", http.StatusBadRequest, errors.New(com + " delete requires 2 arguments")
		}

		sheet, err := db.Open(args[1])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		index, err := strconv.Atoi(args[2])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		if err := sheet.Delete(index); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(sheet.Read())
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "move":
		if len(args) != 4 {
			return []byte{}, "", http.StatusBadRequest, errors.New(com + " swap requires 3 arguments")
		}

		sheet, err := db.Open(args[1])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		index1, err := strconv.Atoi(args[2])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		index2, err := strconv.Atoi(args[3])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		if err := sheet.Move(index1, index2); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(sheet.Read())
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "swap":
		if len(args) != 4 {
			return []byte{}, "", http.StatusBadRequest, errors.New(com + " swap requires 3 arguments")
		}

		sheet, err := db.Open(args[1])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		index1, err := strconv.Atoi(args[2])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		index2, err := strconv.Atoi(args[3])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		if err := sheet.Swap(index1, index2); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(sheet.Read())
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "write":
		if len(args) < 4 {
			return []byte{}, "", http.StatusBadRequest, errors.New(com + " write requires at least 3 arguments")
		}

		sheet, err := db.Open(args[1])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		index, err := strconv.Atoi(args[2])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		record, err := sheet.Open(index)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		record.Write(args[3:])

		jsonBytes, err := json.Marshal(record.Read())
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "modify":
		if len(args) != 5 {
			return []byte{}, "", http.StatusBadRequest, errors.New(com + " modify requires at least 4 arguments")
		}

		sheet, err := db.Open(args[1])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		index, err := strconv.Atoi(args[2])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		record, err := sheet.Open(index)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		keyIndex := slices.Index(record.Headers(), args[3])
		if keyIndex < 0 {
			return []byte{}, "", http.StatusBadRequest, errors.New("invalid record key: " + args[3])
		}

		record.Modify(keyIndex, args[4])

		jsonBytes, err := json.Marshal(record.Read())
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	default:
	}

	return []byte{}, "", http.StatusBadRequest, errors.New("db operation should be header, read, add, delete, move, swap, write or modify")
}
