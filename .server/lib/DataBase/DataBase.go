package DataBase

import (
	"errors"
	"fmt"
	"io/fs"
	"os"
	"slices"
	"strconv"
	"strings"
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

	errDB struct {
		ErrIndexNotFound, ErrSheetNotFound, ErrInvalidDataLenght, ErrInvalidDataContent error
	}
)

var ErrDB = errDB{
	ErrSheetNotFound:      errors.New("sheet not found"),
	ErrIndexNotFound:      errors.New("index not found"),
	ErrInvalidDataLenght:  errors.New("invalid data lenght"),
	ErrInvalidDataContent: errors.New("invalid data content"),
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

	fs.WalkDir(os.DirFS(db.path+"/"+db.name), ".", func(path string, dir fs.DirEntry, err error) error {
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
	})

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

	fs.WalkDir(os.DirFS(db.path+"/"+db.name), ".", func(path string, dir fs.DirEntry, err error) error {
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
	})

	return errs
}

// Open an sheet for interaction.
// Does not need to be closed.
func (db *DataBase) Open(sheet string) (*Sheet, error) {
	if _, ok := db.sheets[sheet]; !ok {
		return &Sheet{}, ErrDB.ErrSheetNotFound
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
		return &Record{}, ErrDB.ErrIndexNotFound
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
	for i := 0; i < len(sheet.records); i++ {
		rawSheet = append(rawSheet, sheet.records[i].data)
	}

	return rawSheet
}

// Add record to sheet.
func (sheet *Sheet) Add(data []string) error {
	if len(sheet.headers) != len(data) {
		return ErrDB.ErrInvalidDataLenght
	}

	for _, s := range data {
		if strings.Contains(s, sheet.seperator) {
			return ErrDB.ErrInvalidDataContent
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
		return ErrDB.ErrIndexNotFound
	}

	sheet.records = append(sheet.records[:index], sheet.records[index+1:]...)

	return nil
}

// Move record in sheet.
func (sheet *Sheet) Move(index1 int, index2 int) error {
	if index1 < 0 || len(sheet.records)-1 < index1 || index2 < 0 || len(sheet.records)-1 < index2 {
		return ErrDB.ErrIndexNotFound
	}

	record := sheet.records[index1]
	sheet.records = append(sheet.records[:index1], sheet.records[index1+1:]...)
	sheet.records = slices.Insert(sheet.records, index2, record)

	return nil
}

// Swap 2 records in sheet.
func (sheet *Sheet) Swap(index1 int, index2 int) error {
	if index1 < 0 || len(sheet.records)-1 < index1 || index2 < 0 || len(sheet.records)-1 < index2 {
		return ErrDB.ErrIndexNotFound
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
		return ErrDB.ErrInvalidDataLenght
	}

	for _, s := range data {
		if strings.Contains(s, record.seperator) {
			return ErrDB.ErrInvalidDataContent
		}
	}

	record.data = data

	return nil
}

// Modify value in record.
func (record *Record) Modify(index int, data string) error {
	if index < 0 || len(record.data)-1 < index {
		return ErrDB.ErrIndexNotFound
	}

	if strings.Contains(data, record.seperator) {
		return ErrDB.ErrInvalidDataContent
	}

	record.data[index] = data

	return nil
}

// Check if record has value.
func (record *Record) Has(index int) bool {
	return index > 0 && index < len(record.data)-1
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
