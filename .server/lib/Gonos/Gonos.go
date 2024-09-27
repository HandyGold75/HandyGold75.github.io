package Gonos

import (
	"encoding/xml"
	"errors"
	"strings"
)

type errSonos struct {
	ErrUnexpectedResponse error
	ErrInvalidPlayMode    error
}

var ErrSonos = errSonos{
	ErrUnexpectedResponse: errors.New("unexpected response"),
	ErrInvalidPlayMode:    errors.New("invalid play mode"),
}

func NewZonePlayer(ipAddress string) *ZonePlayer {
	return &ZonePlayer{IpAddress: ipAddress}
}

// Endpoints

const TRANSPORT_ENDPOINT = `/MediaRenderer/AVTransport/Control`
const RENDERING_ENDPOINT = `/MediaRenderer/RenderingControl/Control`
const DEVICE_ENDPOINT = `/DeviceProperties/Control`
const CONTENT_DIRECTORY_ENDPOINT = `/MediaServer/ContentDirectory/Control`

// General

const SOAP_TEMPLATE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>{body}</s:Body></s:Envelope>`

var PLAYMODES = map[string][3]bool{
	// "MODE": [2]bool{shuffle, repeat, repeat_one}
	"NORMAL":             {false, false, false},
	"SHUFFLE_NOREPEAT":   {true, false, false},
	"SHUFFLE":            {true, true, false},
	"REPEAT_ALL":         {false, true, false},
	"SHUFFLE_REPEAT_ONE": {true, false, true},
	"REPEAT_ONE":         {false, false, true},
}

var PLAYMODES_REVERSED = func() map[[3]bool]string {
	PMS := map[[3]bool]string{}
	for k, v := range PLAYMODES {
		PMS[v] = k
	}
	return PMS
}()

// TODO: Discovery

const PLAYER_SEARCH = `M-SEARCH * HTTP/1.1
HOST: 239.255.255.250:reservedSSDPport
MAN: ssdp:discover
MX: 1
ST: urn:schemas-upnp-org:device:ZonePlayer:1`

const MCAST_GRP = "239.255.255.250"
const MCAST_PORT = 1900

// State

const GET_CUR_TRANSPORT_ACTION = `"urn:schema-upnp-org:service:AVTransport:1#GetTransportInfo"`
const GET_CUR_TRANSPORT_BODY = `<u:GetTransportInfo xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:GetTransportInfo></s:Body></s:Envelope>`

// Play

const PLAY_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#Play"`
const PLAY_BODY = `<u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Play>`
const PLAY_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:PlayResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:PlayResponse></s:Body></s:Envelope>`

// Pause

const PAUSE_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#Pause"`
const PAUSE_BODY = `<u:Pause xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Pause>`
const PAUSE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:PauseResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:PauseResponse></s:Body></s:Envelope>`

// Stop

const STOP_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#Stop"`
const STOP_BODY = `<u:Stop xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Stop>`
const STOP_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:StopResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:StopResponse></s:Body></s:Envelope>`

// Next

const NEXT_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#Next"`
const NEXT_BODY = `<u:Next xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Next>`
const NEXT_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:NextResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:NextResponse></s:Body></s:Envelope>`

// Previous

const PREV_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#Previous"`
const PREV_BODY = `<u:Previous xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Previous>`
const PREV_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:PreviousResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:PreviousResponse></s:Body></s:Envelope>`

// Seek

const SEEK_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#Seek"`
const SEEK_BODY_TEMPLATE = `<u:Seek xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Unit>REL_TIME</Unit><Target>{timestamp}</Target></u:Seek>`
const SEEK_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SeekResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:SeekResponse></s:Body></s:Envelope>`

// Mute

const SET_MUTE_ACTION = `"urn:schemas-upnp-org:service:RenderingControl:1#SetMute"`
const SET_MUTE_BODY_TEMPLATE = `<u:SetMute xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel><DesiredMute>{mute}</DesiredMute></u:SetMute>`
const SET_MUTE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetMuteResponse xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"></u:SetMuteResponse></s:Body></s:Envelope>`

const GET_MUTE_ACTION = `"urn:schemas-upnp-org:service:RenderingControl:1#GetMute"`
const GET_MUTE_BODY = `<u:GetMute xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetMute>`

// Volume

const SET_VOLUME_ACTION = `"urn:schemas-upnp-org:service:RenderingControl:1#SetVolume"`
const SET_VOLUME_BODY_TEMPLATE = `<u:SetVolume xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel><DesiredVolume>{volume}</DesiredVolume></u:SetVolume>`
const SET_VOLUME_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetVolumeResponse xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"></u:SetVolumeResponse></s:Body></s:Envelope>`

const GET_VOLUME_ACTION = `"urn:schemas-upnp-org:service:RenderingControl:1#GetVolume"`
const GET_VOLUME_BODY = `<u:GetVolume xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetVolume>`

// Bass

const SET_BASS_ACTION = `"urn:schemas-upnp-org:service:RenderingControl:1#SetBass"`
const SET_BASS_BODY_TEMPLATE = `<u:SetBass xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><DesiredBass>{bass}</DesiredBass></u:SetBass>`
const SET_BASS_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetBassResponse xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"></u:SetBassResponse></s:Body></s:Envelope>`

const GET_BASS_ACTION = `"urn:schemas-upnp-org:service:RenderingControl:1#GetBass"`
const GET_BASS_BODY = `<u:GetBass xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetBass>`

// Treble

const SET_TREBLE_ACTION = `"urn:schemas-upnp-org:service:RenderingControl:1#SetTreble"`
const SET_TREBLE_BODY_TEMPLATE = `<u:SetTreble xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><DesiredTreble>{treble}</DesiredTreble></u:SetTreble>`
const SET_TREBLE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetTrebleResponse xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"></u:SetTrebleResponse></s:Body></s:Envelope>`

const GET_TREBLE_ACTION = `"urn:schemas-upnp-org:service:RenderingControl:1#GetTreble"`
const GET_TREBLE_BODY = `<u:GetTreble xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetTreble>`

// Loudness

const SET_LOUDNESS_ACTION = `"urn:schemas-upnp-org:service:RenderingControl:1#SetLoudness"`
const SET_LOUDNESS_BODY_TEMPLATE = `<u:SetLoudness xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel><DesiredLoudness>{loudness}</DesiredLoudness></u:SetLoudness>`
const SET_LOUDNESS_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetLoudnessResponse xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"></u:SetLoudnessResponse></s:Body></s:Envelope>`

const GET_LOUDNESS_ACTION = `"urn:schemas-upnp-org:service:RenderingControl:1#GetLoudness"`
const GET_LOUDNESS_BODY = `<u:GetLoudness xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetLoudness>`

// Led State

const SET_LEDSTATE_ACTION = `"urn:schemas-upnp-org:service:DeviceProperties:1#SetLEDState"`
const SET_LEDSTATE_BODY_TEMPLATE = `<u:SetLEDState xmlns:u="urn:schemas-upnp-org:service:DeviceProperties:1"><DesiredLEDState>{ledstate}</DesiredLEDState>`
const SET_LEDSTATE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetLEDStateResponse xmlns:u="urn:schemas-upnp-org:service:DeviceProperties:1"></u:SetLEDStateResponse></s:Body></s:Envelope>`

const GET_LEDSTATE_ACTION = `"urn:schemas-upnp-org:service:DeviceProperties:1#GetLEDState"`
const GET_LEDSTATE_BODY = `<u:GetLEDState xmlns:u="urn:schemas-upnp-org:service:DeviceProperties:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetLEDState>`

const SET_PLAYER_NAME_ACTION = `"urn:schemas-upnp-org:service:DeviceProperties:1#SetZoneAttributes"`
const SET_PLAYER_NAME_BODY_TEMPLATE = `"<u:SetZoneAttributes xmlns:u="urn:schemas-upnp-org:service:DeviceProperties:1"><DesiredZoneName>{playername}</DesiredZoneName><DesiredIcon/><DesiredConfiguration/></u:SetZoneAttributes>"`
const SET_PLAYER_NAME_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetZoneAttributesResponse xmlns:u="urn:schemas-upnp-org:service:DeviceProperties:1"></u:SetZoneAttributesResponse></s:Body></s:Envelope>`

const GET_PLAYER_NAME_ACTION = `"urn:schemas-upnp-org:service:DeviceProperties:1#GetZoneAttributes"`
const GET_PLAYER_NAME_BODY = `<u:GetZoneAttributes xmlns:u="urn:schemas-upnp-org:service:DeviceProperties:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetZoneAttributes>`

// Group

const JOIN_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"`
const JOIN_BODY_TEMPLATE = `<u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>x-rincon:{master_uid}</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI>`
const JOIN_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetAVTransportURIResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:SetAVTransportURIResponse></s:Body></s:Envelope>`

const UNJOIN_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#BecomeCoordinatorOfStandaloneGroup"`
const UNJOIN_BODY = `<u:BecomeCoordinatorOfStandaloneGroup xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:BecomeCoordinatorOfStandaloneGroup>`
const UNJOIN_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:BecomeCoordinatorOfStandaloneGroupResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:BecomeCoordinatorOfStandaloneGroupResponse></s:Body></s:Envelope>`

// Play Mode

const SET_PLAYMODE_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#SetPlayMode"`
const SET_PLAYMODE_BODY_TEMPLATE = `<u:SetPlayMode xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><NewPlayMode>{playmode}</NewPlayMode></u:GetTransportSettings>`
const SET_PLAYMODE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetPlayModeResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:SetPlayModeResponse></s:Body></s:Envelope>`

const GET_PLAYMODE_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#GetTransportSettings"`
const GET_PLAYMODE_BODY = `<u:GetTransportSettings xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:GetTransportSettings>`

// TODO: SetLineIn (Testing)

const SET_LINEIN_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"`
const SET_LINEIN_BODY_TEMPLATE = `<u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>x-rincon-stream:{speaker_uid}</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI>`
const SET_LINEIN_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetAVTransportURIResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:SetAVTransportURIResponse></s:Body></s:Envelope>`

// Current Track

const GET_CUR_TRACK_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#GetPositionInfo"`
const GET_CUR_TRACK_BODY = `<u:GetPositionInfo xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetPositionInfo>`

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

// Que

const PLAY_FROM_QUEUE_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#Seek"`
const PLAY_FROM_QUEUE_BODY_TEMPLATE = `<u:Seek xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Unit>TRACK_NR</Unit><Target>{track}</Target></u:Seek>`
const PLAY_FROM_QUEUE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SeekResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:SeekResponse></s:Body></s:Envelope>`

// TODO: AddToQue (Testing)

const ADD_TO_QUEUE_ACTION = `urn:schemas-upnp-org:service:AVTransport:1#AddURIToQueue`
const ADD_TO_QUEUE_BODY_TEMPLATE = `<u:AddURIToQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><EnqueuedURI>{uri}</EnqueuedURI><EnqueuedURIMetaData></EnqueuedURIMetaData><DesiredFirstTrackNumberEnqueued>{index}</DesiredFirstTrackNumberEnqueued><EnqueueAsNext>{as_next}</EnqueueAsNext></u:AddURIToQueue>`
const ADD_TO_QUEUE_RESPONSE = ``

const REMOVE_FROM_QUEUE_ACTION = `urn:schemas-upnp-org:service:AVTransport:1#RemoveTrackFromQueue`
const REMOVE_FROM_QUEUE_BODY_TEMPLATE = `<u:RemoveTrackFromQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><ObjectID>Q:0/{track}</ObjectID><UpdateID>0</UpdateID></u:RemoveTrackFromQueue>`
const REMOVE_FROM_QUEUE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:RemoveTrackFromQueueResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:RemoveTrackFromQueueResponse></s:Body></s:Envelope>`

const CLEAR_QUEUE_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#RemoveAllTracksFromQueue"`
const CLEAR_QUEUE_BODY = `<u:RemoveAllTracksFromQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:RemoveAllTracksFromQueue>`
const CLEAR_QUEUE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:RemoveAllTracksFromQueueResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:RemoveAllTracksFromQueueResponse></s:Body></s:Envelope>`

const GET_QUEUE_ACTION = `"urn:schemas-upnp-org:service:ContentDirectory:1#Browse"`
const GET_QUEUE_BODY_TEMPLATE = `<u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1"><ObjectID>Q:0</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>dc:title,res,dc:creator,upnp:artist,upnp:album,upnp:albumArtURI</Filter><StartingIndex>{start}</StartingIndex><RequestedCount>{count}</RequestedCount><SortCriteria></SortCriteria></u:Browse>`

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

// Favorites

const GET_FAVORITES_RADIO_STATIONS_ACTION = `"urn:schemas-upnp-org:service:ContentDirectory:1#Browse"`
const GET_FAVORITES_RADIO_STATIONS_BODY_TEMPLATE = `<u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1"><ObjectID>R:0/0</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter><StartingIndex>{start}</StartingIndex><RequestedCount>{count}</RequestedCount><SortCriteria></SortCriteria></u:Browse>`

const GET_FAVORITES_RADIO_SHOWS_ACTION = `"urn:schemas-upnp-org:service:ContentDirectory:1#Browse"`
const GET_FAVORITES_RADIO_SHOWS_BODY_TEMPLATE = `<u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1"><ObjectID>R:0/1</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter><StartingIndex>{start}</StartingIndex><RequestedCount>{count}</RequestedCount><SortCriteria></SortCriteria></u:Browse>`

const GET_FAVORITES_SONOS_ACTION = `"urn:schemas-upnp-org:service:ContentDirectory:1#Browse"`
const GET_FAVORITES_SONOS_BODY_TEMPLATE = `<u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1"><ObjectID>FV:2</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter><StartingIndex>{start}</StartingIndex><RequestedCount>{count}</RequestedCount><SortCriteria></SortCriteria></u:Browse>`

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

// TODO: PlayURI (Testing)

const PLAY_URI_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"`
const PLAY_URI_BODY_TEMPLATE = `<u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>{uri}</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI>`
const PLAY_URI_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetAVTransportURIResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:SetAVTransportURIResponse></s:Body></s:Envelope>`
