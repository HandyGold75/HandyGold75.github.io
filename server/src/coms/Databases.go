package coms

import (
	"HG75/auth"
	"encoding/json"
	"errors"
	"fmt"
	"io/fs"
	"net/http"
	"os"
	"slices"
	"strconv"
	"strings"
	"time"
)

type (
	DataBase struct {
		name         string
		path         string
		template     Template
		seperatorEOK string
		sheets       map[string]*Sheet
	}

	Sheet struct {
		headers   Headers
		seperator string
		records   []Record
	}

	Record struct {
		headers   Headers
		seperator string
		data      []string
	}

	Template map[string]Headers

	Headers []string
)

func (c Coms) databases() Commands {
	return Commands{
		"db-test": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{},
			Description:     "Interact with testing DataBase.",
			AutoComplete:    []string{"header", "read", "add", "delete", "move", "swap", "write", "modify"},
			ArgsDescription: "[header|read|add|delete|move|swap|write|modify] [args?]...",
			ArgsLen:         [2]int{1, 5},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if _, ok := c.dbs[user.UID+"/TestDB"]; !ok {
					err := c.openDB("TestDB", user, Template{
						"Sheet1": []string{"Col1"},
						"Sheet2": []string{"Col1", "Col2"},
						"Sheet3": []string{"Col1", "Col2", "Col3"},
						"Sheet4": []string{"Col1", "Col2", "Col3", "Col4"},
					})
					if err != nil {
						return []byte{}, "", http.StatusInternalServerError, err
					}
				}
				return dbInterface(c.dbs[user.UID+"/TestDB"], "db-test", args...)
			},
		},
		"db-asset": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{},
			Description:     "Interact with testing DataBase.",
			AutoComplete:    []string{"header", "read", "add", "delete", "move", "swap", "write", "modify"},
			ArgsDescription: "[header|read|add|delete|move|swap|write|modify] [args?]...",
			ArgsLen:         [2]int{1, 5},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if _, ok := c.dbs[user.UID+"/AssetDB"]; !ok {
					err := c.openDB("AssetDB", user, Template{
						"Devices": []string{"Name", "Brand", "Device", "Series", "S/N", "MAC-WiFi", "MAC-Eth", "DOP", "EOL", "Modified", "Notes"},
						"Assets":  []string{"Name", "Brand", "Asset", "Series", "S/N", "DOP", "EOL", "Modified", "Notes"},
						"Servers": []string{"Name", "Brand", "Server", "Series", "S/N", "MAC", "DOP", "EOL", "Modified", "Notes"},
						"Parts":   []string{"Name", "Brand", "Part", "Series", "S/N", "DOP", "EOL", "Modified", "Notes"},
					})
					if err != nil {
						return []byte{}, "", http.StatusInternalServerError, err
					}
				}
				return dbInterface(c.dbs[user.UID+"/AssetDB"], "db-asset", args...)
			},
		},
		"db-license": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{},
			Description:     "Interact with license DataBase.",
			AutoComplete:    []string{"header", "read", "add", "delete", "move", "swap", "write", "modify"},
			ArgsDescription: "[header|read|add|delete|move|swap|write|modify] [args?]...",
			ArgsLen:         [2]int{1, 5},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if _, ok := c.dbs[user.UID+"/LicenseDB"]; !ok {
					err := c.openDB("LicenseDB", user, Template{
						"Licenses": []string{"Name", "Product", "Key", "URL", "DOP", "EOL", "Cost", "Auto Renew", "Modified", "Notes"},
					})
					if err != nil {
						return []byte{}, "", http.StatusInternalServerError, err
					}
				}
				return dbInterface(c.dbs[user.UID+"/LicenseDB"], "db-license", args...)
			},
		},
		"db-query": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{},
			Description:     "Interact with query DataBase.",
			AutoComplete:    []string{"header", "read", "add", "delete", "move", "swap", "write", "modify"},
			ArgsDescription: "[header|read|add|delete|move|swap|write|modify] [args?]...",
			ArgsLen:         [2]int{1, 5},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if _, ok := c.dbs[user.UID+"/QueryDB"]; !ok {
					err := c.openDB("QueryDB", user, Template{
						"Links":   []string{"Img", "Text", "Url", "Cat", "Modified"},
						"Contact": []string{"Img", "Text", "Url", "Modified"},
					})
					if err != nil {
						return []byte{}, "", http.StatusInternalServerError, err
					}
				}
				return dbInterface(c.dbs[user.UID+"/QueryDB"], "db-query", args...)
			},
		},
	}
}

func (c Coms) openDB(name string, user auth.User, template Template) error {
	c.lgr.Log("debug", user.Username, "loading", name)
	dir, err := os.Executable()
	if err != nil {
		return Errors.PathNotFound
	}
	fileSplit := strings.Split(strings.ReplaceAll(dir, "\\", "/"), "/")
	path := strings.Join(fileSplit[:len(fileSplit)-1], "/") + "/data/db/" + user.UID

	f, err := os.Stat(path)
	if err != nil || !f.IsDir() {
		fileSplit := strings.Split(strings.ReplaceAll(path, "\\", "/"), "/")
		err := os.MkdirAll(strings.Join(fileSplit[:len(fileSplit)-1], "/"), os.ModePerm)
		if err != nil {
			return err
		}
	}

	db, err := New(name, path, template)
	if err != nil {
		return errors.New("failed creating or loading database")
	}

	for _, err := range db.Load() {
		c.lgr.Log("error", user.Username, "failed", "loading db "+name+"; error: "+err.Error())
	}

	c.dbs[user.UID+"/"+name] = db

	time.AfterFunc(time.Until(time.Now().Add(time.Minute*time.Duration(c.cfg.DataBaseOpenTimeout))), func() {
		c.lgr.Log("debug", user.Username, "dumping", name)
		for _, err := range c.dbs[user.UID+"/"+name].Dump() {
			c.lgr.Log("error", user.Username, "failed", "dumping db "+name+"; error: "+err.Error())
		}
		delete(c.dbs, user.UID+"/"+name)
		c.lgr.Log("low", user.Username, "dumped", name)
	})
	c.lgr.Log("low", user.Username, "loaded", name)
	return nil
}

// Create new db.
// Will load from exisitng db on disk or create a new db on disk.
func New(name string, path string, template Template) (*DataBase, error) {
	return NewDB(name, path, "<EOK>", template)
}

// Same as NewDB but with more options.
func NewDB(name string, path string, eokSeperator string, template Template) (*DataBase, error) {
	db := &DataBase{
		name:         name,
		path:         path,
		seperatorEOK: eokSeperator,
		template:     template,
		sheets:       map[string]*Sheet{},
	}

	if err := db.prepFolders(); err != nil {
		return &DataBase{}, err
	}

	return db, nil
}

// Get db name.
func (db *DataBase) GetName() string {
	return db.name
}

// Get db path.
func (db *DataBase) GetPath() string {
	return db.path
}

// Get db template.
func (db *DataBase) GetTemplate() Template {
	return db.template
}

// Load disk to memory.
// Warning: this will override changes made since last dump!
func (db *DataBase) Load() []error {
	errs := []error{}
	db.sheets = map[string]*Sheet{}

	if err := fs.WalkDir(os.DirFS(db.path+"/"+db.name), ".", func(path string, dir fs.DirEntry, err error) error {
		if err != nil || path == "." {
			return err
		}

		if (strings.Count(path, "/") == 1 && dir.IsDir()) || strings.Count(path, "/") > 1 || (strings.Count(path, "/") < 1 && !dir.IsDir()) {
			errs = append(errs, errors.New("invalid path of file found, removing: "+path))
			if err := os.RemoveAll(db.path + "/" + db.name + "/" + path); err != nil {
				errs = append(errs, err)
			}
			return nil
		}

		if dir.IsDir() || strings.Count(path, "/") < 1 {
			if _, ok := db.template[path]; !ok {
				errs = append(errs, errors.New("unknown path found, removing: "+path))
				if err := os.RemoveAll(db.path + "/" + db.name + "/" + path); err != nil {
					errs = append(errs, err)
				}
				return nil
			}

			db.sheets[path] = &Sheet{
				headers:   db.template[path],
				seperator: db.seperatorEOK,
			}
			return nil
		}

		pathSplit := strings.Split(path, "/")
		key, record := pathSplit[0], pathSplit[1]
		if _, ok := db.template[key]; !ok {
			errs = append(errs, errors.New("unknown key found, removing: "+key))
			if err := os.RemoveAll(db.path + "/" + db.name + "/" + key); err != nil {
				errs = append(errs, err)
			}
			return nil
		}

		fileData, err := os.ReadFile(db.path + "/" + db.name + "/" + key + "/" + record)
		if err != nil {
			return err
		}

		recordData := strings.Split(string(fileData), db.seperatorEOK)
		if len(recordData) != len(db.template[key]) {
			errs = append(errs, errors.New("invalid record found, removing: "+key+"/"+key))
			if err := os.RemoveAll(db.path + "/" + db.name + "/" + key + "/" + record); err != nil {
				errs = append(errs, err)
			}
			return nil
		}

		sheet := db.sheets[key]
		sheet.records = append(sheet.records, Record{
			headers:   sheet.headers,
			seperator: db.seperatorEOK,
			data:      recordData,
		})
		db.sheets[key] = sheet

		return nil
	}); err != nil {
		errs = append(errs, err)
	}

	return errs
}

// Dump memory to disk.
func (db *DataBase) Dump() []error {
	errs := []error{}

	if err := db.prepFolders(); err != nil {
		return append(errs, err)
	}

	for key := range db.sheets {
		for i, record := range db.sheets[key].records {
			file, err := os.OpenFile(db.path+"/"+db.name+"/"+key+"/"+fmt.Sprintf("%09d", i), os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0740)
			if err != nil {
				errs = append(errs, err)
				continue
			}

			if _, err := file.Write([]byte(strings.Join(record.data, db.seperatorEOK))); err != nil {
				errs = append(errs, err)
			}
			if err := file.Sync(); err != nil {
				errs = append(errs, err)
			}
			if err := file.Close(); err != nil {
				errs = append(errs, err)
			}
		}
	}

	if err := fs.WalkDir(os.DirFS(db.path+"/"+db.name), ".", func(path string, dir fs.DirEntry, err error) error {
		if err != nil || path == "." {
			return err
		}

		if (strings.Count(path, "/") == 1 && dir.IsDir()) || strings.Count(path, "/") > 1 || (strings.Count(path, "/") < 1 && !dir.IsDir()) {
			errs = append(errs, errors.New("invalid path of file found, removing: "+path))
			if err := os.RemoveAll(db.path + "/" + db.name + "/" + path); err != nil {
				errs = append(errs, err)
			}
			return nil
		}

		if dir.IsDir() || strings.Count(path, "/") < 1 {
			if _, ok := db.sheets[path]; !ok {
				errs = append(errs, errors.New("unknown path found, removing: "+path))
				if err := os.RemoveAll(db.path + "/" + db.name + "/" + path); err != nil {
					errs = append(errs, err)
				}
				return nil
			}
			return nil
		}

		pathSplit := strings.Split(path, "/")
		key, record := pathSplit[0], pathSplit[1]
		if _, ok := db.sheets[key]; !ok {
			errs = append(errs, errors.New("unknown key found, removing: "+key))
			if err := os.RemoveAll(db.path + "/" + db.name + "/" + key); err != nil {
				errs = append(errs, err)
			}
			return nil
		}

		recordIndex, err := strconv.Atoi(record)
		if err != nil {
			errs = append(errs, errors.New("invalid record name found, removing: "+record))
			if err := os.RemoveAll(db.path + "/" + db.name + "/" + key + "/" + record); err != nil {
				errs = append(errs, err)
			}
			return nil
		}

		if recordIndex > len(db.sheets[key].records)-1 {
			if err := os.RemoveAll(db.path + "/" + db.name + "/" + key + "/" + record); err != nil {
				errs = append(errs, err)
			}
		}

		return nil
	}); err != nil {
		errs = append(errs, err)
	}

	return errs
}

// Open an sheet for interaction.
// Does not need to be closed.
func (db *DataBase) Open(sheet string) (*Sheet, error) {
	if _, ok := db.sheets[sheet]; !ok {
		return &Sheet{}, Errors.SheetNotFound
	}

	return db.sheets[sheet], nil
}

func (db *DataBase) prepFolders() error {
	allDirs := []string{
		db.path,
		db.path + "/" + db.name,
	}

	for key := range db.template {
		allDirs = append(allDirs, db.path+"/"+db.name+"/"+key)
	}

	for _, dir := range allDirs {
		if _, err := os.Stat(dir); os.IsNotExist(err) {
			if err := os.Mkdir(dir, 0740); err != nil {
				return err
			}
		}
	}

	return nil
}

// Read all sheets from db.
func (db *DataBase) Read() map[string][][]string {
	rawData := map[string][][]string{}
	for name, sheet := range db.sheets {
		rawData[name] = sheet.Read()
	}

	return rawData
}

// Check if db has sheet.
func (db *DataBase) Has(sheet string) bool {
	_, ok := db.sheets[sheet]
	return ok
}

// Open an record for interaction.
// Does not need to be closed.
func (sheet *Sheet) Open(index int) (*Record, error) {
	if index < 0 || len(sheet.records)-1 < index {
		return &Record{}, Errors.IndexNotFound
	}

	return &sheet.records[index], nil
}

// Headers from a sheet.
func (sheet *Sheet) Headers() []string {
	return sheet.headers
}

// Read all records from sheet.
func (sheet *Sheet) Read() [][]string {
	rawSheet := [][]string{}
	for i := range sheet.records {
		rawSheet = append(rawSheet, sheet.records[i].data)
	}

	return rawSheet
}

// Add record to sheet.
func (sheet *Sheet) Add(data []string) error {
	if len(sheet.headers) != len(data) {
		return Errors.InvalidDataLenght
	}

	for _, s := range data {
		if strings.Contains(s, sheet.seperator) {
			return Errors.InvalidDataContent
		}
	}

	sheet.records = append(sheet.records, Record{
		headers:   sheet.headers,
		seperator: sheet.seperator,
		data:      data,
	})

	return nil
}

// Delete record from sheet.
func (sheet *Sheet) Delete(index int) error {
	if index < 0 || len(sheet.records)-1 < index {
		return Errors.IndexNotFound
	}

	sheet.records = slices.Delete(sheet.records, index, index+1)

	return nil
}

// Move record in sheet.
func (sheet *Sheet) Move(index1 int, index2 int) error {
	if index1 < 0 || len(sheet.records)-1 < index1 || index2 < 0 || len(sheet.records)-1 < index2 {
		return Errors.IndexNotFound
	}

	record := sheet.records[index1]
	sheet.records = slices.Delete(sheet.records, index1, index1+1)
	sheet.records = slices.Insert(sheet.records, index2, record)

	return nil
}

// Swap 2 records in sheet.
func (sheet *Sheet) Swap(index1 int, index2 int) error {
	if index1 < 0 || len(sheet.records)-1 < index1 || index2 < 0 || len(sheet.records)-1 < index2 {
		return Errors.IndexNotFound
	}

	record := sheet.records[index1]
	sheet.records[index1] = sheet.records[index2]
	sheet.records[index2] = record

	return nil
}

// Check if sheet has record.
func (sheet *Sheet) Has(index int) bool {
	return index > 0 && index < len(sheet.records)-1
}

// Headers from a record.
func (record *Record) Headers() []string {
	return record.headers
}

// Read all values from record
func (record *Record) Read() []string {
	return record.data
}

// Write new record to record.
func (record *Record) Write(data []string) error {
	if len(record.data) != len(data) {
		return Errors.InvalidDataLenght
	}

	for _, s := range data {
		if strings.Contains(s, record.seperator) {
			return Errors.InvalidDataContent
		}
	}

	record.data = data

	return nil
}

// Modify value in record.
func (record *Record) Modify(index int, data string) error {
	if index < 0 || len(record.data)-1 < index {
		return Errors.IndexNotFound
	}

	if strings.Contains(data, record.seperator) {
		return Errors.InvalidDataContent
	}

	record.data[index] = data

	return nil
}

// Check if record has value.
func (record *Record) Has(index int) bool {
	return index > 0 && index < len(record.data)-1
}

func dbInterface(db *DataBase, com string, args ...string) (con []byte, typ string, code int, err error) {
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
			return jsonBytes, TypeJSON, http.StatusOK, nil
		}

		jsonBytes, err := json.Marshal(template)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		return jsonBytes, TypeJSON, http.StatusOK, nil

	case "read":
		if len(args) == 1 {
			jsonBytes, err := json.Marshal(db.Read())
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return jsonBytes, TypeJSON, http.StatusOK, nil
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

			return jsonBytes, TypeJSON, http.StatusOK, nil
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
		return jsonBytes, TypeJSON, http.StatusOK, nil

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
		return jsonBytes, TypeJSON, http.StatusOK, nil

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
		return jsonBytes, TypeJSON, http.StatusOK, nil

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
		return jsonBytes, TypeJSON, http.StatusOK, nil

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
		return jsonBytes, TypeJSON, http.StatusOK, nil

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
		err = record.Write(args[3:])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		jsonBytes, err := json.Marshal(record.Read())
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		return jsonBytes, TypeJSON, http.StatusOK, nil

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
		err = record.Modify(keyIndex, args[4])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		jsonBytes, err := json.Marshal(record.Read())
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		return jsonBytes, TypeJSON, http.StatusOK, nil

	default:
		return []byte{}, "", http.StatusBadRequest, errors.New("db operation should be header, read, add, delete, move, swap, write or modify")
	}
}
