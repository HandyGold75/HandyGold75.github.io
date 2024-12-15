package Gonos

import (
	"encoding/xml"
	"errors"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"strings"
)

type (
	command struct{ Endpoint, Action, Body, ExpectedResponse, TargetTag string }

	errSonos struct {
		ErrUnexpectedResponse error
		ErrInvalidEndpoint    error
		ErrInvalidPlayMode    error
	}

	ZonePlayer struct {
		IpAddress string
	}
)

var ErrSonos = errSonos{
	ErrUnexpectedResponse: errors.New("unexpected response"),
	ErrInvalidEndpoint:    errors.New("invalid endpoint"),
	ErrInvalidPlayMode:    errors.New("invalid play mode"),
}

// Endpoints

var Endpoints = map[string]string{
	"AVTransport":      `/MediaRenderer/AVTransport/Control`,
	"RenderingControl": `/MediaRenderer/RenderingControl/Control`,
	"DeviceProperties": `/DeviceProperties/Control`,
	"ContentDirectory": `/MediaServer/ContentDirectory/Control`,
}

// const EP_Transport = `/MediaRenderer/AVTransport/Control`
const EP_Rendering = `/MediaRenderer/RenderingControl/Control`
const EP_Device = `/DeviceProperties/Control`
const EP_Content = `/MediaServer/ContentDirectory/Control`

// Playmodes

var Playmodes = map[string][3]bool{
	// "MODE": [2]bool{shuffle, repeat, repeat_one}
	"NORMAL":             {false, false, false},
	"SHUFFLE_NOREPEAT":   {true, false, false},
	"SHUFFLE":            {true, true, false},
	"REPEAT_ALL":         {false, true, false},
	"SHUFFLE_REPEAT_ONE": {true, false, true},
	"REPEAT_ONE":         {false, false, true},
}
var PlaymodesReversed = func() map[[3]bool]string {
	PMS := map[[3]bool]string{}
	for k, v := range Playmodes {
		PMS[v] = k
	}
	return PMS
}()

func boolToInt(b bool) int {
	if b {
		return 1
	}
	return 0
}

// Create new ZonePlayer for controling a Sonos speaker.
func NewZonePlayer(ipAddress string) *ZonePlayer {
	return &ZonePlayer{IpAddress: ipAddress}
}

// Get current transport state.
func (zp *ZonePlayer) GetState() (string, error) {
	return zp.sendCommand("AVTransport", "GetTransportInfo", "", false, "CurrentTransportState") // TODO: Verify response
}

// Same as GetState but converts to bool based on current state
func (zp *ZonePlayer) GetPlay() (bool, error) {
	state, err := zp.GetState()
	return state == "PLAYING", err
}

// Start track.
func (zp *ZonePlayer) Play() error {
	_, err := zp.sendCommand("AVTransport", "Play", "<Speed>1</Speed>", true, "")
	return err
}

// Same as GetState but converts to bool based on current state
func (zp *ZonePlayer) GetPause() (bool, error) {
	state, err := zp.GetState()
	return state == "PAUSED_PLAYBACK", err
}

// Pause track.
func (zp *ZonePlayer) Pause() error {
	_, err := zp.sendCommand("AVTransport", "Pause", "<Speed>1</Speed>", true, "")
	return err
}

// Same as GetState but converts to bool based on current state
func (zp *ZonePlayer) GetStop() (bool, error) {
	state, err := zp.GetState()
	return state == "STOPPED", err
}

// Reset track progress and pause.
func (zp *ZonePlayer) Stop() error {
	_, err := zp.sendCommand("AVTransport", "Stop", "<Speed>1</Speed>", true, "")
	return err
}

// Next track.
func (zp *ZonePlayer) Next() error {
	_, err := zp.sendCommand("AVTransport", "Next", "<Speed>1</Speed>", true, "")
	return err
}

// Previous track.
func (zp *ZonePlayer) Previous() error {
	_, err := zp.sendCommand("AVTransport", "Previous", "<Speed>1</Speed>", true, "")
	return err
}

// Set progress.
func (zp *ZonePlayer) Seek(hours int, minutes int, seconds int) error {
	_, err := zp.sendCommand("AVTransport", "Seek", "<Unit>REL_TIME</Unit><Target>"+fmt.Sprintf("%v:%v:%v", hours, minutes, seconds)+"</Target>", true, "")
	return err
}

// Get current volume.
func (zp *ZonePlayer) GetVolume() (int, error) {
	res, err := zp.sendCommandOld(command{Endpoint: EP_Rendering, Action: GET_VOLUME_ACTION, Body: GET_VOLUME_BODY, TargetTag: "CurrentVolume"})
	if err != nil {
		return 0, err
	}
	return strconv.Atoi(res)
}

// Set volume.
func (zp *ZonePlayer) SetVolume(level int) error {
	_, err := zp.sendCommandOld(command{Endpoint: EP_Rendering, Action: SET_VOLUME_ACTION, Body: strings.Replace(SET_VOLUME_BODY_TEMPLATE, "{volume}", strconv.Itoa(max(0, min(100, level))), 1), ExpectedResponse: SET_VOLUME_RESPONSE})
	return err
}

// Get current mute state.
func (zp *ZonePlayer) GetMute() (bool, error) {
	res, err := zp.sendCommandOld(command{Endpoint: EP_Rendering, Action: GET_MUTE_ACTION, Body: GET_MUTE_BODY, TargetTag: "CurrentMute"})
	return res == "1", err
}

// Set mute state.
func (zp *ZonePlayer) SetMute(state bool) error {
	var body string
	if state {
		body = strings.Replace(SET_MUTE_BODY_TEMPLATE, "{mute}", "1", 1)
	} else {
		body = strings.Replace(SET_MUTE_BODY_TEMPLATE, "{mute}", "0", 1)
	}
	_, err := zp.sendCommandOld(command{Endpoint: EP_Rendering, Action: SET_MUTE_ACTION, Body: body, ExpectedResponse: SET_MUTE_RESPONSE})
	return err
}

// Get current bass.
func (zp *ZonePlayer) GetBass() (int, error) {
	res, err := zp.sendCommandOld(command{Endpoint: EP_Rendering, Action: GET_BASS_ACTION, Body: GET_BASS_BODY, TargetTag: "CurrentBass"})
	if err != nil {
		return 0, err
	}
	return strconv.Atoi(res)
}

// Set bass.
func (zp *ZonePlayer) SetBass(level int) error {
	_, err := zp.sendCommandOld(command{Endpoint: EP_Rendering, Action: SET_BASS_ACTION, Body: strings.Replace(SET_BASS_BODY_TEMPLATE, "{bass}", strconv.Itoa(max(-10, min(10, level))), 1), ExpectedResponse: SET_BASS_RESPONSE})
	return err
}

// Get current treble.
func (zp *ZonePlayer) GetTreble() (int, error) {
	res, err := zp.sendCommandOld(command{Endpoint: EP_Rendering, Action: GET_TREBLE_ACTION, Body: GET_TREBLE_BODY, TargetTag: "CurrentTreble"})
	if err != nil {
		return 0, err
	}
	return strconv.Atoi(res)
}

// Set treble.
func (zp *ZonePlayer) SetTreble(level int) error {
	_, err := zp.sendCommandOld(command{Endpoint: EP_Rendering, Action: SET_TREBLE_ACTION, Body: strings.Replace(SET_TREBLE_BODY_TEMPLATE, "{treble}", strconv.Itoa(max(-10, min(10, level))), 1), ExpectedResponse: SET_TREBLE_RESPONSE})
	return err
}

// Get current loudness state.
func (zp *ZonePlayer) GetLoudness() (bool, error) {
	res, err := zp.sendCommandOld(command{Endpoint: EP_Rendering, Action: GET_LOUDNESS_ACTION, Body: GET_LOUDNESS_BODY, TargetTag: "CurrentLoudness"})
	return res == "1", err
}

// Set loudness state.
func (zp *ZonePlayer) SetLoudness(state bool) error {
	var body string
	if state {
		body = strings.Replace(SET_LOUDNESS_BODY_TEMPLATE, "{loudness}", "1", 1)
	} else {
		body = strings.Replace(SET_LOUDNESS_BODY_TEMPLATE, "{loudness}", "0", 1)
	}
	_, err := zp.sendCommandOld(command{Endpoint: EP_Rendering, Action: SET_LOUDNESS_ACTION, Body: body, ExpectedResponse: SET_LOUDNESS_RESPONSE})
	return err
}

// Get current led state.
func (zp *ZonePlayer) GetLedState() (bool, error) {
	res, err := zp.sendCommandOld(command{Endpoint: EP_Device, Action: GET_LEDSTATE_ACTION, Body: GET_LEDSTATE_BODY, TargetTag: "CurrentLEDState"})
	return res == "On", err
}

// Set led state.
func (zp *ZonePlayer) SetLedState(state bool) error {
	var body string
	if state {
		body = strings.Replace(SET_LEDSTATE_BODY_TEMPLATE, "{ledstate}", "On", 1)
	} else {
		body = strings.Replace(SET_LEDSTATE_BODY_TEMPLATE, "{ledstate}", "Off", 1)
	}
	_, err := zp.sendCommandOld(command{Endpoint: EP_Device, Action: SET_LEDSTATE_ACTION, Body: body, ExpectedResponse: SET_LEDSTATE_RESPONSE})
	return err
}

// Get player name.
func (zp *ZonePlayer) GetPlayerName() (string, error) {
	return zp.sendCommandOld(command{Endpoint: EP_Device, Action: GET_PLAYER_NAME_ACTION, Body: GET_PLAYER_NAME_BODY, TargetTag: "CurrentZoneName"})
}

// Set player name.
func (zp *ZonePlayer) SetPlayerName(name string) error {
	_, err := zp.sendCommandOld(command{Endpoint: EP_Device, Action: SET_PLAYER_NAME_ACTION, Body: strings.Replace(SET_PLAYER_NAME_BODY_TEMPLATE, "{playername}", name, 1), ExpectedResponse: SET_PLAYER_NAME_RESPONSE})
	return err
}

// Join player to master. (TODO: Untested)
func (zp *ZonePlayer) JoinPlayer(master_uid string) error {
	_, err := zp.sendCommand("AVTransport", "SetAVTransportURI", "<CurrentURI>x-rincon:"+master_uid+"</CurrentURI><CurrentURIMetaData></CurrentURIMetaData>", true, "")
	return err
}

// Unjoin player. (TODO: Untested)
func (zp *ZonePlayer) UnjoinPlayer() error {
	_, err := zp.sendCommand("AVTransport", "BecomeCoordinatorOfStandaloneGroup", "<Speed>1</Speed>", true, "")
	return err
}

// Get player mode.
func (zp *ZonePlayer) GetPlayMode() (shuffle bool, repeat bool, repeat_one bool, err error) {
	res, err := zp.sendCommand("AVTransport", "GetTransportSettings", "", false, "PlayMode") // TODO: Verify response
	if err != nil {
		return false, false, false, err
	}
	modeBools, ok := Playmodes[res]
	if !ok {
		return false, false, false, ErrSonos.ErrUnexpectedResponse
	}
	return modeBools[0], modeBools[1], modeBools[2], nil
}

// Set player mode.
func (zp *ZonePlayer) SetPlayMode(shuffle bool, repeat bool, repeat_one bool) error {
	mode, ok := PlaymodesReversed[[3]bool{shuffle, repeat, repeat_one}]
	if !ok {
		return ErrSonos.ErrInvalidPlayMode
	}
	_, err := zp.sendCommand("AVTransport", "SetPlayMode", "<NewPlayMode>"+mode+"</NewPlayMode>", true, "")
	return err
}

// Get shuffle mode.
func (zp *ZonePlayer) GetShuffle() (bool, error) {
	shuffle, _, _, err := zp.GetPlayMode()
	return shuffle, err
}

// Set shuffle mode.
func (zp *ZonePlayer) SetShuffle(state bool) error {
	_, repeat, repeat_one, err := zp.GetPlayMode()
	if err != nil {
		return err
	}
	return zp.SetPlayMode(state, repeat, repeat_one)
}

// Get repeat mode.
func (zp *ZonePlayer) GetRepeat() (bool, error) {
	_, repeat, _, err := zp.GetPlayMode()
	return repeat, err
}

// Set repeat mode.
func (zp *ZonePlayer) SetRepeat(state bool) error {
	shuffle, _, repeat_one, err := zp.GetPlayMode()
	if err != nil {
		return err
	}
	return zp.SetPlayMode(shuffle, state, repeat_one && !state)
}

// Get repeat one mode.
func (zp *ZonePlayer) GetRepeatOne() (bool, error) {
	_, _, repeat_one, err := zp.GetPlayMode()
	return repeat_one, err
}

// Set repeat one mode.
func (zp *ZonePlayer) SetRepeatOne(state bool) error {
	shuffle, repeat, _, err := zp.GetPlayMode()
	if err != nil {
		return err
	}
	return zp.SetPlayMode(shuffle, repeat && !state, state)
}

// Set line in. (TODO: Untested)
func (zp *ZonePlayer) SetLineIn(speaker_uid string) error {
	_, err := zp.sendCommand("AVTransport", "SetAVTransportURI", "<CurrentURI>x-rincon-stream:"+speaker_uid+"</CurrentURI><CurrentURIMetaData></CurrentURIMetaData>", true, "")
	return err
}

// Get information about the current track.
func (zp *ZonePlayer) GetTrackInfo() (*TrackInfo, error) {
	trackInfo, err := zp.GetTrackInfoRaw()
	if err != nil {
		return &TrackInfo{}, err
	}
	trackMetaDataItem, err := trackInfo.ParseMetaData()
	if err != nil {
		return &TrackInfo{}, err
	}

	return &TrackInfo{
		QuePosition: trackInfo.Track,
		Duration:    trackInfo.TrackDuration,
		URI:         trackInfo.TrackURI,
		Progress:    trackInfo.RelTime,
		AlbumArtURI: "http://" + zp.IpAddress + ":1400" + trackMetaDataItem.AlbumArtUri,
		Title:       trackMetaDataItem.Title,
		Class:       trackMetaDataItem.Class,
		Creator:     trackMetaDataItem.Creator,
		Album:       trackMetaDataItem.Album,
	}, nil
}

// Same as GetTrackInfo but won't parse the information as much.
func (zp *ZonePlayer) GetTrackInfoRaw() (TrackInfoRaw, error) {
	// type (
	// 	xmlBody struct {
	// 		XMLName                 xml.Name     `xml:"Body"`
	// 		GetPositionInfoResponse TrackInfoRaw `xml:"GetPositionInfoResponse"`
	// 	}
	// 	xmlEnvelope struct {
	// 		XMLName xml.Name `xml:"Envelope"`
	// 		Body    xmlBody  `xml:"Body"`
	// 	}
	// )

	res, err := zp.sendCommand("AVTransport", "GetPositionInfo", "<Channel>Master</Channel>", false, "s:Body")
	if err != nil {
		return TrackInfoRaw{}, err
	}
	trackInfo := TrackInfoRaw{}
	if err := xml.Unmarshal([]byte(res), &trackInfo); err != nil {
		return TrackInfoRaw{}, err
	}
	return trackInfo, nil
}

// Get information about the que.
func (zp *ZonePlayer) GetQueInfo() (*QueInfo, error) {
	queInfo, err := zp.GetQueInfoRaw(0, 0)
	if err != nil {
		return &QueInfo{}, err
	}
	queMetaDataItem, err := queInfo.ParseMetaData()
	if err != nil {
		return &QueInfo{}, err
	}

	tracks := []QueTrack{}
	for _, track := range queMetaDataItem {
		tracks = append(tracks, QueTrack{
			AlbumArtURI: "http://" + zp.IpAddress + ":1400" + track.AlbumArtUri,
			Title:       track.Title,
			Class:       track.Class,
			Creator:     track.Creator,
			Album:       track.Album,
		})
	}
	qi := &QueInfo{
		Count:      queInfo.NumberReturned,
		TotalCount: queInfo.TotalMatches,
		Tracks:     tracks,
	}
	return qi, nil
}

// Same as GetQueInfo but won't parse the information as much.
func (zp *ZonePlayer) GetQueInfoRaw(start int, count int) (QueInfoRaw, error) {
	type (
		xmlBody struct {
			XMLName        xml.Name   `xml:"Body"`
			BrowseResponse QueInfoRaw `xml:"BrowseResponse"`
		}
		xmlEnvelope struct {
			XMLName xml.Name `xml:"Envelope"`
			Body    xmlBody  `xml:"Body"`
		}
	)

	res, err := zp.sendCommandOld(command{Endpoint: EP_Content, Action: GET_QUEUE_ACTION, Body: strings.Replace(strings.Replace(GET_QUEUE_BODY_TEMPLATE, "{start}", strconv.Itoa(start), 1), "{count}", strconv.Itoa(count), 1)})
	if err != nil {
		return QueInfoRaw{}, err
	}
	envelope := xmlEnvelope{}
	if err := xml.Unmarshal([]byte(res), &envelope); err != nil {
		return QueInfoRaw{}, err
	}
	return envelope.Body.BrowseResponse, nil
}

// Get information about the favorites.
func (zp *ZonePlayer) GetFavoritesInfo() (*FavoritesInfo, error) {
	favoritesInfo, err := zp.GetFavoritesInfoRaw(0, 0)
	if err != nil {
		return &FavoritesInfo{}, err
	}
	favoritesMetaDataItem, err := favoritesInfo.ParseMetaData()
	if err != nil {
		return &FavoritesInfo{}, err
	}

	favorites := []FavoritesItem{}
	for _, favorite := range favoritesMetaDataItem {
		favorites = append(favorites, FavoritesItem{
			AlbumArtURI: "http://" + zp.IpAddress + ":1400" + favorite.AlbumArtUri,
			Title:       favorite.Title,
			Description: favorite.Description,
			Class:       favorite.Class,
			Type:        favorite.Type,
		})
	}
	qi := &FavoritesInfo{
		Count:      favoritesInfo.NumberReturned,
		TotalCount: favoritesInfo.TotalMatches,
		Favorites:  favorites,
	}
	return qi, nil
}

// Same as GetFavoritesInfo but won't parse the information as much.
func (zp *ZonePlayer) GetFavoritesInfoRaw(start int, count int) (FavoritesInfoRaw, error) {
	type (
		xmlBody struct {
			XMLName        xml.Name         `xml:"Body"`
			BrowseResponse FavoritesInfoRaw `xml:"BrowseResponse"`
		}
		xmlEnvelope struct {
			XMLName xml.Name `xml:"Envelope"`
			Body    xmlBody  `xml:"Body"`
		}
	)

	res, err := zp.sendCommandOld(command{Endpoint: EP_Content, Action: GET_FAVORITES_SONOS_ACTION, Body: strings.Replace(strings.Replace(GET_FAVORITES_SONOS_BODY_TEMPLATE, "{start}", strconv.Itoa(start), 1), "{count}", strconv.Itoa(count), 1)})
	if err != nil {
		return FavoritesInfoRaw{}, err
	}
	envelope := xmlEnvelope{}
	if err := xml.Unmarshal([]byte(res), &envelope); err != nil {
		return FavoritesInfoRaw{}, err
	}
	return envelope.Body.BrowseResponse, nil
}

// Get information about the favorites radio stations.
func (zp *ZonePlayer) GetFavoritesRadioStationsInfo() (*FavoritesInfo, error) {
	favoritesInfo, err := zp.GetFavoritesRadioStationsInfoRaw(0, 0)
	if err != nil {
		return &FavoritesInfo{}, err
	}
	favoritesMetaDataItem, err := favoritesInfo.ParseMetaData()
	if err != nil {
		return &FavoritesInfo{}, err
	}

	favorites := []FavoritesItem{}
	for _, favorite := range favoritesMetaDataItem {
		favorites = append(favorites, FavoritesItem{
			AlbumArtURI: "http://" + zp.IpAddress + ":1400" + favorite.AlbumArtUri,
			Title:       favorite.Title,
			Description: favorite.Description,
			Class:       favorite.Class,
			Type:        favorite.Type,
		})
	}
	qi := &FavoritesInfo{
		Count:      favoritesInfo.NumberReturned,
		TotalCount: favoritesInfo.TotalMatches,
		Favorites:  favorites,
	}
	return qi, nil
}

// Same as GetFavoritesRadioStationsInfo but won't parse the information as much.
func (zp *ZonePlayer) GetFavoritesRadioStationsInfoRaw(start int, count int) (FavoritesInfoRaw, error) {
	type (
		xmlBody struct {
			XMLName        xml.Name         `xml:"Body"`
			BrowseResponse FavoritesInfoRaw `xml:"BrowseResponse"`
		}
		xmlEnvelope struct {
			XMLName xml.Name `xml:"Envelope"`
			Body    xmlBody  `xml:"Body"`
		}
	)

	res, err := zp.sendCommandOld(command{Endpoint: EP_Content, Action: GET_FAVORITES_RADIO_STATIONS_ACTION, Body: strings.Replace(strings.Replace(GET_FAVORITES_RADIO_STATIONS_BODY_TEMPLATE, "{start}", strconv.Itoa(start), 1), "{count}", strconv.Itoa(count), 1)})
	if err != nil {
		return FavoritesInfoRaw{}, err
	}
	envelope := xmlEnvelope{}
	if err := xml.Unmarshal([]byte(res), &envelope); err != nil {
		return FavoritesInfoRaw{}, err
	}
	return envelope.Body.BrowseResponse, nil
}

// Get information about the favorites radio shows.
func (zp *ZonePlayer) GetFavoritesRadioShowsInfo() (*FavoritesInfo, error) {
	favoritesInfo, err := zp.GetFavoritesRadioShowsInfoRaw(0, 0)
	if err != nil {
		return &FavoritesInfo{}, err
	}
	favoritesMetaDataItem, err := favoritesInfo.ParseMetaData()
	if err != nil {
		return &FavoritesInfo{}, err
	}

	favorites := []FavoritesItem{}
	for _, favorite := range favoritesMetaDataItem {
		favorites = append(favorites, FavoritesItem{
			AlbumArtURI: "http://" + zp.IpAddress + ":1400" + favorite.AlbumArtUri,
			Title:       favorite.Title,
			Description: favorite.Description,
			Class:       favorite.Class,
			Type:        favorite.Type,
		})
	}
	qi := &FavoritesInfo{
		Count:      favoritesInfo.NumberReturned,
		TotalCount: favoritesInfo.TotalMatches,
		Favorites:  favorites,
	}
	return qi, nil
}

// Same as GetFavoritesRadioShowsInfo but won't parse the information as much.
func (zp *ZonePlayer) GetFavoritesRadioShowsInfoRaw(start int, count int) (FavoritesInfoRaw, error) {
	type (
		xmlBody struct {
			XMLName        xml.Name         `xml:"Body"`
			BrowseResponse FavoritesInfoRaw `xml:"BrowseResponse"`
		}
		xmlEnvelope struct {
			XMLName xml.Name `xml:"Envelope"`
			Body    xmlBody  `xml:"Body"`
		}
	)

	res, err := zp.sendCommandOld(command{Endpoint: EP_Content, Action: GET_FAVORITES_RADIO_SHOWS_ACTION, Body: strings.Replace(strings.Replace(GET_FAVORITES_RADIO_SHOWS_BODY_TEMPLATE, "{start}", strconv.Itoa(start), 1), "{count}", strconv.Itoa(count), 1)})
	if err != nil {
		return FavoritesInfoRaw{}, err
	}
	envelope := xmlEnvelope{}
	if err := xml.Unmarshal([]byte(res), &envelope); err != nil {
		return FavoritesInfoRaw{}, err
	}
	return envelope.Body.BrowseResponse, nil
}

// Play from que.
func (zp *ZonePlayer) PlayFromQue(track int) error {
	_, err := zp.sendCommand("AVTransport", "Seek", "<Unit>TRACK_NR</Unit><Target>"+strconv.Itoa(max(1, track))+"</Target>", true, "")
	return err
}

// Remove from que.
func (zp *ZonePlayer) RemoveFromQue(track int) error {
	_, err := zp.sendCommand("AVTransport", "RemoveTrackFromQueue", "<ObjectID>Q:0/"+strconv.Itoa(max(1, track))+"</ObjectID><UpdateID>0</UpdateID>", true, "")
	return err
}

// Add URI to que. (TODO: Untested)
func (zp *ZonePlayer) AddToQue(uri string, index string, next bool) error {
	_, err := zp.sendCommand("AVTransport", "AddURIToQueue", "<EnqueuedURI>"+uri+"</EnqueuedURI><EnqueuedURIMetaData></EnqueuedURIMetaData><DesiredFirstTrackNumberEnqueued>"+index+"</DesiredFirstTrackNumberEnqueued><EnqueueAsNext>"+strconv.Itoa(boolToInt(next))+"</EnqueueAsNext>", false, "") // TODO: Verify response
	return err
}

// Clear que.
func (zp *ZonePlayer) ClearQue() error {
	_, err := zp.sendCommand("AVTransport", "RemoveAllTracksFromQueue", "", true, "")
	return err
}

// Set URI. (TODO: Untested)
func (zp *ZonePlayer) PlayUri(uri string, meta string) error {
	_, err := zp.sendCommand("AVTransport", "SetAVTransportURI", "<CurrentURI>"+uri+"</CurrentURI><CurrentURIMetaData>"+meta+"</CurrentURIMetaData>", true, "")
	return err
}

type (
	TrackInfo struct {
		QuePosition string
		Duration    string
		URI         string
		Progress    string
		AlbumArtURI string
		Title       string
		Class       string
		Creator     string
		Album       string
	}

	TrackInfoRaw struct {
		XMLName       xml.Name `xml:"GetPositionInfoResponse"`
		Track         string
		TrackDuration string
		TrackMetaData string
		TrackURI      string
		RelTime       string
		AbsTime       string
		RelCount      string
		AbsCount      string
	}

	TrackMetaData struct {
		XMLName       xml.Name `xml:"item"`
		Res           string   `xml:"res"`
		StreamContent string   `xml:"streamContent"`
		AlbumArtUri   string   `xml:"albumArtURI"`
		Title         string   `xml:"title"`
		Class         string   `xml:"class"`
		Creator       string   `xml:"creator"`
		Album         string   `xml:"album"`
	}
)

func (track TrackInfoRaw) ParseMetaData() (TrackMetaData, error) {
	type xmlDIDL struct {
		XMLName xml.Name      `xml:"DIDL-Lite"`
		Item    TrackMetaData `xml:"item"`
	}

	tmd := track.TrackMetaData
	tmd = strings.ReplaceAll(tmd, "&quot;", "\"")
	tmd = strings.ReplaceAll(tmd, "&gt;", ">")
	tmd = strings.ReplaceAll(tmd, "&lt;", "<")

	didl := xmlDIDL{}
	if err := xml.Unmarshal([]byte(tmd), &didl); err != nil {
		return TrackMetaData{}, err
	}

	return didl.Item, nil
}

type (
	QueInfo struct {
		Count      string
		TotalCount string
		Tracks     []QueTrack
	}

	QueTrack struct {
		AlbumArtURI string
		Title       string
		Class       string
		Creator     string
		Album       string
	}

	QueInfoRaw struct {
		XMLName        xml.Name `xml:"BrowseResponse"`
		Result         string
		NumberReturned string
		TotalMatches   string
		UpdateID       string
	}

	QueMetaData struct {
		XMLName     xml.Name `xml:"item"`
		Res         string   `xml:"res"`
		AlbumArtUri string   `xml:"albumArtURI"`
		Title       string   `xml:"title"`
		Class       string   `xml:"class"`
		Creator     string   `xml:"creator"`
		Album       string   `xml:"album"`
	}
)

func (que QueInfoRaw) ParseMetaData() ([]QueMetaData, error) {
	type xmlDIDL struct {
		XMLName xml.Name      `xml:"DIDL-Lite"`
		Item    []QueMetaData `xml:"item"`
	}

	tmd := que.Result
	tmd = strings.ReplaceAll(tmd, "&quot;", "\"")
	tmd = strings.ReplaceAll(tmd, "&gt;", ">")
	tmd = strings.ReplaceAll(tmd, "&lt;", "<")

	didl := xmlDIDL{}
	if err := xml.Unmarshal([]byte(tmd), &didl); err != nil {
		return []QueMetaData{}, err
	}

	return didl.Item, nil
}

type (
	FavoritesInfo struct {
		Count      string
		TotalCount string
		Favorites  []FavoritesItem
	}

	FavoritesItem struct {
		AlbumArtURI string
		Title       string
		Description string
		Class       string
		Type        string
	}

	FavoritesInfoRaw struct {
		XMLName        xml.Name `xml:"BrowseResponse"`
		Result         string
		NumberReturned string
		TotalMatches   string
		UpdateID       string
	}

	FavoritesMetaData struct {
		XMLName     xml.Name `xml:"item"`
		Title       string   `xml:"title"`
		Class       string   `xml:"class"`
		Ordinal     string   `xml:"ordinal"`
		Res         string   `xml:"res"`
		AlbumArtUri string   `xml:"albumArtURI"`
		Type        string   `xml:"type"`
		Description string   `xml:"description"`
		ResMD       string   `xml:"resMD"`
	}
)

func (favorites FavoritesInfoRaw) ParseMetaData() ([]FavoritesMetaData, error) {
	type xmlDIDL struct {
		XMLName xml.Name            `xml:"DIDL-Lite"`
		Item    []FavoritesMetaData `xml:"item"`
	}

	tmd := favorites.Result
	tmd = strings.ReplaceAll(tmd, "&quot;", "\"")
	tmd = strings.ReplaceAll(tmd, "&gt;", ">")
	tmd = strings.ReplaceAll(tmd, "&lt;", "<")

	didl := xmlDIDL{}
	if err := xml.Unmarshal([]byte(tmd), &didl); err != nil {
		return []FavoritesMetaData{}, err
	}

	return didl.Item, nil
}

// TODO: delme
func (zp *ZonePlayer) sendCommandOld(c command) (string, error) {
	req, err := http.NewRequest("POST", "http://"+zp.IpAddress+":1400"+c.Endpoint, strings.NewReader(strings.Replace(SOAP_TEMPLATE, "{body}", c.Body, 1)))
	if err != nil {
		return "", err
	}
	req.Header.Add("Content-Type", "text/xml")
	req.Header.Add("SOAPACTION", c.Action)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	result, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	resultStr := string(result[:])

	if c.ExpectedResponse != "" && resultStr != c.ExpectedResponse {
		return resultStr, ErrSonos.ErrUnexpectedResponse
	}
	if c.TargetTag != "" {
		start, end := strings.Index(resultStr, "<"+c.TargetTag+">"), strings.Index(resultStr, "</"+c.TargetTag+">")
		if start == -1 || end == -1 {
			return "", ErrSonos.ErrUnexpectedResponse
		}
		return resultStr[start+len(c.TargetTag)+2 : end], nil
	}
	return resultStr, nil
}

func (zp *ZonePlayer) sendCommand(endpoint string, action string, body string, verifyResponse bool, targetTag string) (string, error) {
	endpointUri, ok := Endpoints[endpoint]
	if !ok {
		return "", ErrSonos.ErrInvalidEndpoint
	}

	req, err := http.NewRequest(
		"POST",
		"http://"+zp.IpAddress+":1400"+endpointUri,
		strings.NewReader(strings.Replace(SOAP_TEMPLATE, "{body}", `<u:`+action+` xmlns:u="urn:schemas-upnp-org:service:`+endpoint+`:1"><InstanceID>0</InstanceID>`+body+`</u:`+action+`>`, 1)),
	)
	if err != nil {
		return "", err
	}
	req.Header.Add("Content-Type", "text/xml")
	req.Header.Add("SOAPACTION", "urn:schemas-upnp-org:service:"+endpoint+":1#"+action)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	result, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	resultStr := string(result[:])

	if verifyResponse && resultStr != `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:`+action+`Response xmlns:u="urn:schemas-upnp-org:service:`+endpoint+`:1"></u:`+action+`Response></s:Body></s:Envelope>` {
		fmt.Print("\r\n" + resultStr)
		fmt.Print("\r\n" + `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:` + action + `Response xmlns:u="urn:schemas-upnp-org:service:` + endpoint + `:1"></u:` + action + `Response></s:Body></s:Envelope>`)
		fmt.Print("\r\n")
		fmt.Print("\r\n")
		return resultStr, ErrSonos.ErrUnexpectedResponse
	} else if targetTag != "" {
		start, end := strings.Index(resultStr, "<"+targetTag+">"), strings.Index(resultStr, "</"+targetTag+">")
		if start == -1 || end == -1 {
			return resultStr, ErrSonos.ErrUnexpectedResponse
		}
		return resultStr[start+len(targetTag)+2 : end], nil
	}
	return resultStr, nil
}
