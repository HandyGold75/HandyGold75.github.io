package Gonos

import (
	"encoding/xml"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"strings"
)

type (
	ZonePlayer struct {
		IpAddress string
	}
)

// Get current transport state.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetState() (bool, error) {
	state, err := zp.GetStateRaw()
	if err != nil {
		return false, err
	}

	if state == "PLAYING" {
		return true, nil
	}
	return false, nil
}

// Same as GetState but doesn't convert the state to bool.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetStateRaw() (string, error) {
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, GET_CUR_TRANSPORT_ACTION, GET_CUR_TRANSPORT_BODY)
	if err != nil {
		return "", err
	}

	return zp.extractTagData("CurrentTransportState", res), nil
}

// Start track.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) Play() error {
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, PLAY_ACTION, PLAY_BODY)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, PLAY_RESPONSE)
}

// Pause track.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) Pause() error {
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, PAUSE_ACTION, PAUSE_BODY)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, PAUSE_RESPONSE)
}

// Reset track progress and pause.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) Stop() error {
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, STOP_ACTION, STOP_BODY)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, STOP_RESPONSE)
}

// Next track.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) Next() error {
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, NEXT_ACTION, NEXT_BODY)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, NEXT_RESPONSE)
}

// Previous track.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) Previous() error {
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, PREV_ACTION, PREV_BODY)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, PREV_RESPONSE)
}

// Set progress.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) Seek(hours int, minutes int, seconds int) error {
	body := strings.Replace(SEEK_BODY_TEMPLATE, "{timestamp}", fmt.Sprintf("%v:%v:%v", hours, minutes, seconds), 1)
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, SEEK_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, SEEK_RESPONSE)
}

// Get current volume.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetVolume() (int, error) {
	res, err := zp.sendCommand(RENDERING_ENDPOINT, GET_VOLUME_ACTION, GET_VOLUME_BODY)
	if err != nil {
		return 0, err
	}

	level, err := strconv.Atoi(zp.extractTagData("CurrentVolume", res))
	if err != nil {
		return 0, err
	}

	return level, nil
}

// Set volume.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) SetVolume(level int) error {
	level = max(0, min(100, level))

	body := strings.Replace(SET_VOLUME_BODY_TEMPLATE, "{volume}", strconv.Itoa(level), 1)
	res, err := zp.sendCommand(RENDERING_ENDPOINT, SET_VOLUME_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, SET_VOLUME_RESPONSE)
}

// Get current mute state.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetMute() (bool, error) {
	res, err := zp.sendCommand(RENDERING_ENDPOINT, GET_MUTE_ACTION, GET_MUTE_BODY)
	if err != nil {
		return false, err
	}

	state, err := strconv.Atoi(zp.extractTagData("CurrentMute", res))
	if err != nil {
		return false, err
	}

	if state > 0 {
		return true, nil
	}
	return false, nil
}

// Set mute state.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) SetMute(state bool) error {
	s := "0"
	if state {
		s = "1"
	}

	body := strings.Replace(SET_MUTE_BODY_TEMPLATE, "{mute}", s, 1)
	res, err := zp.sendCommand(RENDERING_ENDPOINT, SET_MUTE_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, SET_MUTE_RESPONSE)
}

// Get current bass.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetBass() (int, error) {
	res, err := zp.sendCommand(RENDERING_ENDPOINT, GET_BASS_ACTION, GET_BASS_BODY)
	if err != nil {
		return 0, err
	}

	level, err := strconv.Atoi(zp.extractTagData("CurrentBass", res))
	if err != nil {
		return 0, err
	}

	return level, nil
}

// Set bass.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) SetBass(level int) error {
	level = max(-10, min(10, level))

	body := strings.Replace(SET_BASS_BODY_TEMPLATE, "{bass}", strconv.Itoa(level), 1)
	res, err := zp.sendCommand(RENDERING_ENDPOINT, SET_BASS_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, SET_BASS_RESPONSE)
}

// Get current treble.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetTreble() (int, error) {
	res, err := zp.sendCommand(RENDERING_ENDPOINT, GET_TREBLE_ACTION, GET_TREBLE_BODY)
	if err != nil {
		return 0, err
	}

	level, err := strconv.Atoi(zp.extractTagData("CurrentTreble", res))
	if err != nil {
		return 0, err
	}

	return level, nil
}

// Set treble.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) SetTreble(level int) error {
	level = max(-10, min(10, level))

	body := strings.Replace(SET_TREBLE_BODY_TEMPLATE, "{treble}", strconv.Itoa(level), 1)
	res, err := zp.sendCommand(RENDERING_ENDPOINT, SET_TREBLE_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, SET_TREBLE_RESPONSE)
}

// Get current loudness state.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetLoudness() (bool, error) {
	res, err := zp.sendCommand(RENDERING_ENDPOINT, GET_LOUDNESS_ACTION, GET_LOUDNESS_BODY)
	if err != nil {
		return false, err
	}

	state, err := strconv.Atoi(zp.extractTagData("CurrentLoudness", res))
	if err != nil {
		return false, err
	}

	if state > 0 {
		return true, nil
	}
	return false, nil
}

// Set loudness state.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) SetLoudness(state bool) error {
	s := "0"
	if state {
		s = "1"
	}

	body := strings.Replace(SET_LOUDNESS_BODY_TEMPLATE, "{loudness}", s, 1)
	res, err := zp.sendCommand(RENDERING_ENDPOINT, SET_LOUDNESS_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, SET_LOUDNESS_RESPONSE)
}

// Get current led state.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetLedState() (bool, error) {
	res, err := zp.sendCommand(DEVICE_ENDPOINT, GET_LEDSTATE_ACTION, GET_LEDSTATE_BODY)
	if err != nil {
		return false, err
	}

	state := zp.extractTagData("CurrentLEDState", res)

	if state == "On" {
		return true, nil
	}
	return false, nil
}

// Set led state.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) SetLedState(state bool) error {
	s := "Off"
	if state {
		s = "On"
	}

	body := strings.Replace(SET_LEDSTATE_BODY_TEMPLATE, "{ledstate}", s, 1)
	res, err := zp.sendCommand(DEVICE_ENDPOINT, SET_LEDSTATE_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, SET_LEDSTATE_RESPONSE)
}

// Get player name.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetPlayerName() (string, error) {
	res, err := zp.sendCommand(DEVICE_ENDPOINT, GET_PLAYER_NAME_ACTION, GET_PLAYER_NAME_BODY)
	if err != nil {
		return "", err
	}

	name := zp.extractTagData("CurrentZoneName", res)

	return name, nil
}

// Set player name.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) SetPlayerName(name string) error {
	body := strings.Replace(SET_PLAYER_NAME_BODY_TEMPLATE, "{playername}", name, 1)
	res, err := zp.sendCommand(DEVICE_ENDPOINT, SET_PLAYER_NAME_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, SET_PLAYER_NAME_RESPONSE)
}

// Join player to master. (Untested)
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) JoinPlayer(master_uid string) error {
	body := strings.Replace(JOIN_BODY_TEMPLATE, "{master_uid}", master_uid, 1)
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, JOIN_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, JOIN_RESPONSE)
}

// Unjoin player. (Untested)
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) UnjoinPlayer() error {
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, UNJOIN_ACTION, UNJOIN_BODY)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, UNJOIN_RESPONSE)
}

// Get player mode.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetPlayMode() (string, error) {
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, GET_PLAYMODE_ACTION, GET_PLAYMODE_BODY)
	if err != nil {
		return "", err
	}

	mode := zp.extractTagData("PlayMode", res)

	return mode, nil
}

// Set player mode.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) SetPlayMode(shuffle bool, repeat bool, repeat_one bool) error {
	mode, ok := PLAYMODES_REVERSED[[3]bool{shuffle, repeat, repeat_one}]
	if !ok {
		return ErrSonos.ErrInvalidPlayMode
	}

	body := strings.Replace(SET_PLAYMODE_BODY_TEMPLATE, "{playmode}", mode, 1)
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, SET_PLAYMODE_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, SET_PLAYMODE_RESPONSE)
}

// Get shuffle mode.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetShuffle() (bool, error) {
	mode, err := zp.GetPlayMode()
	if err != nil {
		return false, err
	}

	modeBools, ok := PLAYMODES[mode]
	if !ok {
		return false, ErrSonos.ErrUnexpectedResponse
	}

	return modeBools[0], nil
}

// Set shuffle mode.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) SetShuffle(state bool) error {
	mode, err := zp.GetPlayMode()
	if err != nil {
		return err
	}

	modeBools, ok := PLAYMODES[mode]
	if !ok {
		return ErrSonos.ErrUnexpectedResponse
	}

	return zp.SetPlayMode(state, modeBools[1], modeBools[2])
}

// Get repeat mode.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetRepeat() (bool, error) {
	mode, err := zp.GetPlayMode()
	if err != nil {
		return false, err
	}

	modeBools, ok := PLAYMODES[mode]
	if !ok {
		return false, ErrSonos.ErrUnexpectedResponse
	}

	return modeBools[1], nil
}

// Set repeat mode.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) SetRepeat(state bool) error {
	mode, err := zp.GetPlayMode()
	if err != nil {
		return err
	}

	modeBools, ok := PLAYMODES[mode]
	if !ok {
		return ErrSonos.ErrUnexpectedResponse
	}

	repeatOne := modeBools[2]
	if state && repeatOne {
		repeatOne = false
	}

	return zp.SetPlayMode(modeBools[0], state, repeatOne)
}

// Get repeat one mode.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetRepeatOne() (bool, error) {
	mode, err := zp.GetPlayMode()
	if err != nil {
		return false, err
	}

	modeBools, ok := PLAYMODES[mode]
	if !ok {
		return false, ErrSonos.ErrUnexpectedResponse
	}

	return modeBools[2], nil
}

// Set repeat one mode.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) SetRepeatOne(state bool) error {
	mode, err := zp.GetPlayMode()
	if err != nil {
		return err
	}

	modeBools, ok := PLAYMODES[mode]
	if !ok {
		return ErrSonos.ErrUnexpectedResponse
	}

	repeat := modeBools[1]
	if state && repeat {
		repeat = false
	}

	return zp.SetPlayMode(modeBools[0], repeat, state)
}

// Set line in. (untested)
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) SetLineIn(speaker_uid string) error {
	body := strings.Replace(SET_LINEIN_BODY_TEMPLATE, "{speaker_uid}", speaker_uid, 1)
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, SET_LINEIN_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, SET_LINEIN_RESPONSE)
}

// Get information about the current track.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetTrackInfo() (*TrackInfo, error) {
	trackInfo, err := zp.GetTrackInfoRaw()
	if err != nil {
		return &TrackInfo{}, err
	}

	trackMetaDataItem, err := trackInfo.ParseMetaData()
	if err != nil {
		return &TrackInfo{}, err
	}

	quePos, err := strconv.Atoi(trackInfo.Track)
	if err != nil {
		return &TrackInfo{}, err
	}

	ti := &TrackInfo{
		QuePosition: strconv.Itoa(quePos - 1),
		Duration:    trackInfo.TrackDuration,
		URI:         trackInfo.TrackURI,
		Progress:    trackInfo.RelTime,
		AlbumArtURI: "http://" + zp.IpAddress + ":1400" + trackMetaDataItem.AlbumArtUri,
		Title:       trackMetaDataItem.Title,
		Class:       trackMetaDataItem.Class,
		Creator:     trackMetaDataItem.Creator,
		Album:       trackMetaDataItem.Album,
	}

	return ti, nil
}

// Same as GetTrackInfo but won't parse the information as much.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) GetTrackInfoRaw() (TrackInfoRaw, error) {
	type (
		xmlBody struct {
			XMLName                 xml.Name     `xml:"Body"`
			GetPositionInfoResponse TrackInfoRaw `xml:"GetPositionInfoResponse"`
		}

		xmlEnvelope struct {
			XMLName xml.Name `xml:"Envelope"`
			Body    xmlBody  `xml:"Body"`
		}
	)

	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, GET_CUR_TRACK_ACTION, GET_CUR_TRACK_BODY)
	if err != nil {
		return TrackInfoRaw{}, err
	}

	envelope := xmlEnvelope{}
	if err := xml.Unmarshal([]byte(res), &envelope); err != nil {
		return TrackInfoRaw{}, err
	}

	return envelope.Body.GetPositionInfoResponse, nil
}

// Get information about the que.
//
// Error is returened when a request fails or if a unexpected response is returned.
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
//
// Error is returened when a request fails or if a unexpected response is returned.
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

	body := strings.Replace(GET_QUEUE_BODY_TEMPLATE, "{start}", strconv.Itoa(start), 1)
	body = strings.Replace(body, "{count}", strconv.Itoa(count), 1)

	res, err := zp.sendCommand(CONTENT_DIRECTORY_ENDPOINT, GET_QUEUE_ACTION, body)
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
//
// Error is returened when a request fails or if a unexpected response is returned.
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
//
// Error is returened when a request fails or if a unexpected response is returned.
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

	body := strings.Replace(GET_FAVORITES_SONOS_BODY_TEMPLATE, "{start}", strconv.Itoa(start), 1)
	body = strings.Replace(body, "{count}", strconv.Itoa(count), 1)

	res, err := zp.sendCommand(CONTENT_DIRECTORY_ENDPOINT, GET_FAVORITES_SONOS_ACTION, body)
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
//
// Error is returened when a request fails or if a unexpected response is returned.
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
//
// Error is returened when a request fails or if a unexpected response is returned.
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

	body := strings.Replace(GET_FAVORITES_RADIO_STATIONS_BODY_TEMPLATE, "{start}", strconv.Itoa(start), 1)
	body = strings.Replace(body, "{count}", strconv.Itoa(count), 1)

	res, err := zp.sendCommand(CONTENT_DIRECTORY_ENDPOINT, GET_FAVORITES_RADIO_STATIONS_ACTION, body)
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
//
// Error is returened when a request fails or if a unexpected response is returned.
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
//
// Error is returened when a request fails or if a unexpected response is returned.
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

	body := strings.Replace(GET_FAVORITES_RADIO_SHOWS_BODY_TEMPLATE, "{start}", strconv.Itoa(start), 1)
	body = strings.Replace(body, "{count}", strconv.Itoa(count), 1)

	res, err := zp.sendCommand(CONTENT_DIRECTORY_ENDPOINT, GET_FAVORITES_RADIO_SHOWS_ACTION, body)
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
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) PlayFromQue(track int) error {
	track = max(0, track)

	body := strings.Replace(PLAY_FROM_QUEUE_BODY_TEMPLATE, "{track}", strconv.Itoa(track+1), 1)
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, PLAY_FROM_QUEUE_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, PLAY_FROM_QUEUE_RESPONSE)
}

// Remove from que.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) RemoveFromQue(track int) error {
	track = max(0, track)

	body := strings.Replace(REMOVE_FROM_QUEUE_BODY_TEMPLATE, "{track}", strconv.Itoa(track+1), 1)
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, REMOVE_FROM_QUEUE_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, REMOVE_FROM_QUEUE_RESPONSE)
}

// Add URI to que. (Untested)
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) AddToQue(uri string, index string, next bool) error {
	n := "0"
	if next {
		n = "1"
	}

	body := strings.Replace(ADD_TO_QUEUE_BODY_TEMPLATE, "{uri}", uri, 1)
	body = strings.Replace(body, "{index}", index, 1)
	body = strings.Replace(body, "{as_next}", n, 1)
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, ADD_TO_QUEUE_ACTION, body)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, ADD_TO_QUEUE_RESPONSE)
}

// Clear que.
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) ClearQue() error {
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, CLEAR_QUEUE_ACTION, CLEAR_QUEUE_BODY)
	if err != nil {
		return err
	}

	return zp.verifyResponse(res, CLEAR_QUEUE_RESPONSE)
}

// Set que. (Untested)
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) SetQue(uri string) error {
	body := strings.Replace(PLAY_URI_BODY_TEMPLATE, "{uri}", uri, 1)
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, PLAY_URI_ACTION, body)
	if err != nil {
		return err
	}

	fmt.Println(res)

	return zp.verifyResponse(res, PLAY_URI_RESPONSE)
}

// Set URI. (Untested)
//
// Error is returened when a request fails or if a unexpected response is returned.
func (zp *ZonePlayer) PlayUri(uri string, meta string) error {
	body := strings.Replace(PLAY_URI_BODY_TEMPLATE, "{uri}", uri, 1)
	res, err := zp.sendCommand(TRANSPORT_ENDPOINT, PLAY_URI_ACTION, body)
	if err != nil {
		return err
	}

	fmt.Println(res)

	return zp.verifyResponse(res, PLAY_URI_RESPONSE)
}

func (zp *ZonePlayer) sendCommand(endPoint string, action string, body string) (string, error) {
	req, err := http.NewRequest("POST", "http://"+zp.IpAddress+":1400"+endPoint, strings.NewReader(strings.Replace(SOAP_TEMPLATE, "{body}", body, 1)))
	if err != nil {
		return "", err
	}

	req.Header.Add("Content-Type", "text/xml")
	req.Header.Add("SOAPACTION", action)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	result, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	return string(result[:]), err
}

func (zp *ZonePlayer) extractTagData(tag string, xml string) string {
	openTag := "<" + tag + ">"
	closeTag := "</" + tag + ">"
	start := strings.Index(xml, openTag)
	end := strings.Index(xml, closeTag)

	if start == -1 || end == -1 {
		return ""
	}

	result := xml[start+len(openTag) : end]

	return result
}

func (zp *ZonePlayer) verifyResponse(res string, exp string) error {
	if res != exp {
		return ErrSonos.ErrUnexpectedResponse
	}
	return nil
}
