package Gonos

import (
	"encoding/xml"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"strconv"
	"strings"
	"time"
)

type (
	command    struct{ Endpoint, Action, Body, ExpectedResponse, TargetTag string }
	errSonos   struct{ ErrUnexpectedResponse, ErrDiscoverZonePlayer, ErrTimeout, ErrInvalidEndpoint, ErrInvalidPlayMode error }
	ZonePlayer struct{ IpAddress string }
)

var ErrSonos = errSonos{
	ErrUnexpectedResponse: errors.New("unexpected response"),
	ErrDiscoverZonePlayer: errors.New("unable to discover zone player"),
	ErrTimeout:            errors.New("timeout"),
	ErrInvalidEndpoint:    errors.New("invalid endpoint"),
	ErrInvalidPlayMode:    errors.New("invalid play mode"),
}

var Endpoints = map[string]string{
	"AVTransport":      "/MediaRenderer/AVTransport/Control",
	"RenderingControl": "/MediaRenderer/RenderingControl/Control",
	"DeviceProperties": "/DeviceProperties/Control",
	"ContentDirectory": "/MediaServer/ContentDirectory/Control",
}
var EndpointsBodyPrefix = map[string]string{
	"AVTransport":      "<InstanceID>0</InstanceID>",
	"RenderingControl": "<InstanceID>0</InstanceID><Channel>Master</Channel>",
	"DeviceProperties": "<InstanceID>0</InstanceID><Channel>Master</Channel>",
	"ContentDirectory": "",
}

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

func boolTo10(b bool) string {
	if b {
		return "1"
	}
	return "0"
}
func boolToOnOff(b bool) string {
	if b {
		return "On"
	}
	return "Off"
}

// Create new ZonePlayer for controling a Sonos speaker.
func NewZonePlayer(ipAddress string) *ZonePlayer {
	return &ZonePlayer{IpAddress: ipAddress}
}

// Create new ZonePlayer using discovery controling a Sonos speaker. (TODO: Broken)
func DiscoverZonePlayer() (*ZonePlayer, error) {
	conn, err := net.DialUDP("udp", nil, &net.UDPAddr{IP: net.IPv4(239, 255, 255, 250), Port: 1900})
	if err != nil {
		return &ZonePlayer{}, err
	}
	defer conn.Close()

	c := make(chan string)
	go func() {
		buf := make([]byte, 1024)
		n, addr, err := conn.ReadFrom(buf)
		if err != nil {
			c <- ""
			return
		}
		fmt.Println(addr)
		fmt.Println("---")
		fmt.Println(string(buf[:n]))
		c <- addr.String()
	}()

	_, err = conn.Write([]byte("M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 5\r\nST: urn:schemas-upnp-org:device:ZonePlayer:1\r\n\r\n"))
	if err != nil {
		return &ZonePlayer{}, err
	}

	select {
	case addr := <-c:
		if addr == "" {
			return &ZonePlayer{}, ErrSonos.ErrDiscoverZonePlayer
		}
		return &ZonePlayer{IpAddress: addr}, nil

	case <-time.After(time.Second * 5):
		return &ZonePlayer{}, ErrSonos.ErrTimeout
	}
}

// func main() {
// 	_, err := DiscoverZonePlayer()
// 	if err != nil {
// 		fmt.Println(err)
// 	}
// 	// fmt.Println(out)
// }

// Get current transport state.
func (zp *ZonePlayer) GetState() (string, error) {
	return zp.sendCommand("AVTransport", "GetTransportInfo", "", "CurrentTransportState")
}

// Same as GetState but converts to bool based on current state
func (zp *ZonePlayer) GetPlay() (bool, error) {
	state, err := zp.GetState()
	return state == "PLAYING", err
}

// Start track.
func (zp *ZonePlayer) Play() error {
	_, err := zp.sendCommand("AVTransport", "Play", "<Speed>1</Speed>", "")
	return err
}

// Same as GetState but converts to bool based on current state
func (zp *ZonePlayer) GetPause() (bool, error) {
	state, err := zp.GetState()
	return state == "PAUSED_PLAYBACK", err
}

// Pause track.
func (zp *ZonePlayer) Pause() error {
	_, err := zp.sendCommand("AVTransport", "Pause", "<Speed>1</Speed>", "")
	return err
}

// Same as GetState but converts to bool based on current state
func (zp *ZonePlayer) GetStop() (bool, error) {
	state, err := zp.GetState()
	return state == "STOPPED", err
}

// Reset track progress and pause.
func (zp *ZonePlayer) Stop() error {
	_, err := zp.sendCommand("AVTransport", "Stop", "<Speed>1</Speed>", "")
	return err
}

// Next track.
func (zp *ZonePlayer) Next() error {
	_, err := zp.sendCommand("AVTransport", "Next", "<Speed>1</Speed>", "")
	return err
}

// Previous track.
func (zp *ZonePlayer) Previous() error {
	_, err := zp.sendCommand("AVTransport", "Previous", "<Speed>1</Speed>", "")
	return err
}

// Set progress.
func (zp *ZonePlayer) Seek(hours int, minutes int, seconds int) error {
	_, err := zp.sendCommand("AVTransport", "Seek", "<Unit>REL_TIME</Unit><Target>"+fmt.Sprintf("%v:%v:%v", hours, minutes, seconds)+"</Target>", "")
	return err
}

// Get current volume.
func (zp *ZonePlayer) GetVolume() (int, error) {
	res, err := zp.sendCommand("RenderingControl", "GetVolume", "", "CurrentVolume")
	if err != nil {
		return 0, err
	}
	return strconv.Atoi(res)
}

// Set volume.
func (zp *ZonePlayer) SetVolume(level int) error {
	_, err := zp.sendCommand("RenderingControl", "SetVolume", "<DesiredVolume>"+strconv.Itoa(max(0, min(100, level)))+"</DesiredVolume>", "")
	return err
}

// Get current mute state.
func (zp *ZonePlayer) GetMute() (bool, error) {
	res, err := zp.sendCommand("RenderingControl", "GetMute", "", "CurrentMute")
	return res == "1", err
}

// Set mute state.
func (zp *ZonePlayer) SetMute(state bool) error {
	_, err := zp.sendCommand("RenderingControl", "SetMute", "<DesiredMute>"+boolTo10(state)+"</DesiredMute>", "")
	return err
}

// Get current bass.
func (zp *ZonePlayer) GetBass() (int, error) {
	res, err := zp.sendCommand("RenderingControl", "GetBass", "", "CurrentBass")
	if err != nil {
		return 0, err
	}
	return strconv.Atoi(res)
}

// Set bass.
func (zp *ZonePlayer) SetBass(level int) error {
	_, err := zp.sendCommand("RenderingControl", "SetBass", "<DesiredBass>"+strconv.Itoa(max(-10, min(10, level)))+"</DesiredBass>", "")
	return err
}

// Get current treble.
func (zp *ZonePlayer) GetTreble() (int, error) {
	res, err := zp.sendCommand("RenderingControl", "GetTreble", "", "CurrentTreble")
	if err != nil {
		return 0, err
	}
	return strconv.Atoi(res)
}

// Set treble.
func (zp *ZonePlayer) SetTreble(level int) error {
	_, err := zp.sendCommand("RenderingControl", "SetTreble", "<DesiredTreble>"+strconv.Itoa(max(-10, min(10, level)))+"</DesiredTreble>", "")
	return err
}

// Get current loudness state.
func (zp *ZonePlayer) GetLoudness() (bool, error) {
	res, err := zp.sendCommand("RenderingControl", "GetLoudness", "", "CurrentLoudness")
	return res == "1", err
}

// Set loudness state.
func (zp *ZonePlayer) SetLoudness(state bool) error {
	_, err := zp.sendCommand("RenderingControl", "SetLoudness", "<DesiredLoudness>"+boolTo10(state)+"</DesiredLoudness>", "")
	return err
}

// Get current led state.
func (zp *ZonePlayer) GetLedState() (bool, error) {
	res, err := zp.sendCommand("DeviceProperties", "GetLEDState", "", "CurrentLEDState")
	return res == "On", err
}

// Set led state.
func (zp *ZonePlayer) SetLedState(state bool) error {
	_, err := zp.sendCommand("DeviceProperties", "SetLEDState", "<DesiredLEDState>"+boolToOnOff(state)+"</DesiredLEDState>", "")
	return err
}

// Get player name.
func (zp *ZonePlayer) GetPlayerName() (string, error) {
	return zp.sendCommand("DeviceProperties", "GetZoneAttributes", "", "CurrentZoneName")
}

// Set player name. (TODO: Untested)
func (zp *ZonePlayer) SetPlayerName(name string) error {
	_, err := zp.sendCommand("DeviceProperties", "SetZoneAttributes", "<DesiredZoneName>"+name+"</DesiredZoneName>", "")
	return err
}

// Set player icon. (TODO: Untested)
func (zp *ZonePlayer) SetPlayerIcon(icon string) error {
	_, err := zp.sendCommand("DeviceProperties", "SetZoneAttributes", "<DesiredIcon>"+icon+"</DesiredIcon/>", "")
	return err
}

// Set player config. (TODO: Untested)
func (zp *ZonePlayer) SetPlayeConfig(config string) error {
	_, err := zp.sendCommand("DeviceProperties", "SetZoneAttributes", "<DesiredConfiguration>"+config+"</DesiredConfiguration>", "")
	return err
}

// Join player to master. (TODO: Untested)
func (zp *ZonePlayer) JoinPlayer(master_uid string) error {
	_, err := zp.sendCommand("AVTransport", "SetAVTransportURI", "<CurrentURI>x-rincon:"+master_uid+"</CurrentURI><CurrentURIMetaData></CurrentURIMetaData>", "")
	return err
}

// Unjoin player. (TODO: Untested)
func (zp *ZonePlayer) UnjoinPlayer() error {
	_, err := zp.sendCommand("AVTransport", "BecomeCoordinatorOfStandaloneGroup", "<Speed>1</Speed>", "")
	return err
}

// Get player mode.
func (zp *ZonePlayer) GetPlayMode() (shuffle bool, repeat bool, repeat_one bool, err error) {
	res, err := zp.sendCommand("AVTransport", "GetTransportSettings", "", "PlayMode")
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
	_, err := zp.sendCommand("AVTransport", "SetPlayMode", "<NewPlayMode>"+mode+"</NewPlayMode>", "")
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
	_, err := zp.sendCommand("AVTransport", "SetAVTransportURI", "<CurrentURI>x-rincon-stream:"+speaker_uid+"</CurrentURI><CurrentURIMetaData></CurrentURIMetaData>", "")
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
	res, err := zp.sendCommand("AVTransport", "GetPositionInfo", "", "s:Body")
	if err != nil {
		return TrackInfoRaw{}, err
	}
	trackInfoRaw := TrackInfoRaw{}
	if err := xml.Unmarshal([]byte(res), &trackInfoRaw); err != nil {
		return TrackInfoRaw{}, err
	}
	return trackInfoRaw, nil
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
	res, err := zp.sendCommand("ContentDirectory", "Browse", "<ObjectID>Q:0</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>dc:title,res,dc:creator,upnp:artist,upnp:album,upnp:albumArtURI</Filter><StartingIndex>"+strconv.Itoa(start)+"</StartingIndex><RequestedCount>"+strconv.Itoa(count)+"</RequestedCount><SortCriteria></SortCriteria>", "s:Body")
	if err != nil {
		return QueInfoRaw{}, err
	}
	queInfoRaw := QueInfoRaw{}
	if err := xml.Unmarshal([]byte(res), &queInfoRaw); err != nil {
		return QueInfoRaw{}, err
	}
	return queInfoRaw, nil
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
	res, err := zp.sendCommand("ContentDirectory", "Browse", "<ObjectID>FV:2</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter><StartingIndex>"+strconv.Itoa(start)+"</StartingIndex><RequestedCount>"+strconv.Itoa(count)+"</RequestedCount><SortCriteria></SortCriteria>", "s:Body")
	if err != nil {
		return FavoritesInfoRaw{}, err
	}
	favoritesInfoRaw := FavoritesInfoRaw{}
	if err := xml.Unmarshal([]byte(res), &favoritesInfoRaw); err != nil {
		return FavoritesInfoRaw{}, err
	}
	return favoritesInfoRaw, nil
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
	res, err := zp.sendCommand("ContentDirectory", "Browse", "<ObjectID>R:0/0</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter><StartingIndex>"+strconv.Itoa(start)+"</StartingIndex><RequestedCount>"+strconv.Itoa(count)+"</RequestedCount><SortCriteria></SortCriteria>", "s:Body")
	if err != nil {
		return FavoritesInfoRaw{}, err
	}
	favoritesInfoRaw := FavoritesInfoRaw{}
	if err := xml.Unmarshal([]byte(res), &favoritesInfoRaw); err != nil {
		return FavoritesInfoRaw{}, err
	}
	return favoritesInfoRaw, nil
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

	res, err := zp.sendCommand("ContentDirectory", "Browse", "<ObjectID>R:0/1</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter><StartingIndex>"+strconv.Itoa(start)+"</StartingIndex><RequestedCount>"+strconv.Itoa(count)+"</RequestedCount><SortCriteria></SortCriteria>", "s:Body")
	if err != nil {
		return FavoritesInfoRaw{}, err
	}
	favoritesInfoRaw := FavoritesInfoRaw{}
	if err := xml.Unmarshal([]byte(res), &favoritesInfoRaw); err != nil {
		return FavoritesInfoRaw{}, err
	}
	return favoritesInfoRaw, nil
}

// Play from que.
func (zp *ZonePlayer) PlayFromQue(track int) error {
	_, err := zp.sendCommand("AVTransport", "Seek", "<Unit>TRACK_NR</Unit><Target>"+strconv.Itoa(max(1, track))+"</Target>", "")
	return err
}

// Remove from que.
func (zp *ZonePlayer) RemoveFromQue(track int) error {
	_, err := zp.sendCommand("AVTransport", "RemoveTrackFromQueue", "<ObjectID>Q:0/"+strconv.Itoa(max(1, track))+"</ObjectID><UpdateID>0</UpdateID>", "")
	return err
}

// Add URI to que. (TODO: Untested)
func (zp *ZonePlayer) AddToQue(uri string, index string, next bool) error {
	_, err := zp.sendCommand("AVTransport", "AddURIToQueue", "<EnqueuedURI>"+uri+"</EnqueuedURI><EnqueuedURIMetaData></EnqueuedURIMetaData><DesiredFirstTrackNumberEnqueued>"+index+"</DesiredFirstTrackNumberEnqueued><EnqueueAsNext>"+boolTo10(next)+"</EnqueueAsNext>", "")
	return err
}

// Clear que.
func (zp *ZonePlayer) ClearQue() error {
	_, err := zp.sendCommand("AVTransport", "RemoveAllTracksFromQueue", "", "")
	return err
}

// Set URI. (TODO: Untested)
func (zp *ZonePlayer) PlayUri(uri string, meta string) error {
	_, err := zp.sendCommand("AVTransport", "SetAVTransportURI", "<CurrentURI>"+uri+"</CurrentURI><CurrentURIMetaData>"+meta+"</CurrentURIMetaData>", "")
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

func (zp *ZonePlayer) sendCommand(endpoint string, action string, body string, targetTag string) (string, error) {
	endpointUri, ok := Endpoints[endpoint]
	if !ok {
		return "", ErrSonos.ErrInvalidEndpoint
	}
	endpointBodyPrefix, ok := EndpointsBodyPrefix[endpoint]
	if !ok {
		return "", ErrSonos.ErrInvalidEndpoint
	}

	req, err := http.NewRequest(
		"POST",
		"http://"+zp.IpAddress+":1400"+endpointUri,
		strings.NewReader(`<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:`+action+` xmlns:u="urn:schemas-upnp-org:service:`+endpoint+`:1">`+endpointBodyPrefix+body+`</u:`+action+`></s:Body></s:Envelope>`),
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

	if targetTag != "" {
		start, end := strings.Index(resultStr, "<"+targetTag+">"), strings.Index(resultStr, "</"+targetTag+">")
		if start == -1 || end == -1 {
			return resultStr, ErrSonos.ErrUnexpectedResponse
		}
		return resultStr[start+len(targetTag)+2 : end], nil
	}

	if resultStr != `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:`+action+`Response xmlns:u="urn:schemas-upnp-org:service:`+endpoint+`:1"></u:`+action+`Response></s:Body></s:Envelope>` {
		fmt.Print("\r\n" + resultStr)
		fmt.Print("\r\n" + `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:` + action + `Response xmlns:u="urn:schemas-upnp-org:service:` + endpoint + `:1"></u:` + action + `Response></s:Body></s:Envelope>`)
		fmt.Print("\r\n")
		fmt.Print("\r\n")
		return resultStr, ErrSonos.ErrUnexpectedResponse
	}

	return resultStr, nil
}
