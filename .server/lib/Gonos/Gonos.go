package Gonos

type (
	SonosRequest struct {
		Action, Body, Response string
	}
)

// endpoint -> AVTransport
// action -> Play
// body -> <Speed>1</Speed>
// response ->
func NewSonosRequest(endpoint, action, body string) *SonosRequest {
	return &SonosRequest{
		Action:   "urn:schemas-upnp-org:service:" + endpoint + ":1#" + action,
		Body:     `<u:` + action + ` xmlns:u="urn:schemas-upnp-org:service:` + endpoint + `:1"><InstanceID>0</InstanceID>` + body + `</u:` + action + `>`,
		Response: `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schema:encodingStyle="http://schemass.xmlsoap.org/soap/encoding/"><s:Body><u:` + action + `Response xmlns:u="urn:schemas-upnp-org:service:` + endpoint + `:1"></u:` + action + `Response></s:Body></s:Envelope>`,
	}
}

// General

const SOAP_TEMPLATE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>{body}</s:Body></s:Envelope>`

// TODO: Discovery

const PLAYER_SEARCH = `M-SEARCH * HTTP/1.1
HOST: 239.255.255.250:reservedSSDPport
MAN: ssdp:discover
MX: 1
ST: urn:schemas-upnp-org:device:ZonePlayer:1`
const MCAST_GRP = "239.255.255.250"
const MCAST_PORT = 1900

// Shorts

const A_Prefix = `urn:schemas-upnp-org:service:`
const A_Transport = `AVTransport:1`
const A_Rendering = `RenderingControl:1`
const A_Device = `DeviceProperties:1`
const A_Content = `ContentDirectory:1`

// State

// const GET_CUR_TRANSPORT_ACTION = A_Prefix + A_Transport + `#GetTransportInfo`
// const GET_CUR_TRANSPORT_BODY = `<u:GetTransportInfo xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID></u:GetTransportInfo></s:Body></s:Envelope>`

// Play

// const PLAY_ACTION = A_Prefix + A_Transport + `#Play`
// const PLAY_BODY = `<u:Play xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><Speed>1</Speed></u:Play>`
// const PLAY_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:PlayResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:PlayResponse></s:Body></s:Envelope>`

// Pause

// const PAUSE_ACTION = A_Prefix + A_Transport + `#Pause`
// const PAUSE_BODY = `<u:Pause xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><Speed>1</Speed></u:Pause>`
// const PAUSE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:PauseResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:PauseResponse></s:Body></s:Envelope>`

// Stop

// const STOP_ACTION = A_Prefix + A_Transport + `#Stop`
// const STOP_BODY = `<u:Stop xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><Speed>1</Speed></u:Stop>`
// const STOP_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:StopResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:StopResponse></s:Body></s:Envelope>`

// Next

// const NEXT_ACTION = A_Prefix + A_Transport + `#Next`
// const NEXT_BODY = `<u:Next xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><Speed>1</Speed></u:Next>`
// const NEXT_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:NextResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:NextResponse></s:Body></s:Envelope>`

// Previous

// const PREV_ACTION = A_Prefix + A_Transport + `#Previous`
// const PREV_BODY = `<u:Previous xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><Speed>1</Speed></u:Previous>`
// const PREV_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:PreviousResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:PreviousResponse></s:Body></s:Envelope>`

// Seek

// const SEEK_ACTION = A_Prefix + A_Transport + `#Seek`
// const SEEK_BODY_TEMPLATE = `<u:Seek xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><Unit>REL_TIME</Unit><Target>{timestamp}</Target></u:Seek>`
// const SEEK_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SeekResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:SeekResponse></s:Body></s:Envelope>`

// Mute

const SET_MUTE_ACTION = A_Prefix + A_Rendering + `#SetMute`
const SET_MUTE_BODY_TEMPLATE = `<u:SetMute xmlns:u="` + A_Prefix + A_Rendering + `"><InstanceID>0</InstanceID><Channel>Master</Channel><DesiredMute>{mute}</DesiredMute></u:SetMute>`
const SET_MUTE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetMuteResponse xmlns:u="` + A_Prefix + A_Rendering + `"></u:SetMuteResponse></s:Body></s:Envelope>`

const GET_MUTE_ACTION = A_Prefix + A_Rendering + `#GetMute`
const GET_MUTE_BODY = `<u:GetMute xmlns:u="` + A_Prefix + A_Rendering + `"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetMute>`

// Volume

const SET_VOLUME_ACTION = A_Prefix + A_Rendering + `#SetVolume`
const SET_VOLUME_BODY_TEMPLATE = `<u:SetVolume xmlns:u="` + A_Prefix + A_Rendering + `"><InstanceID>0</InstanceID><Channel>Master</Channel><DesiredVolume>{volume}</DesiredVolume></u:SetVolume>`
const SET_VOLUME_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetVolumeResponse xmlns:u="` + A_Prefix + A_Rendering + `"></u:SetVolumeResponse></s:Body></s:Envelope>`

const GET_VOLUME_ACTION = A_Prefix + A_Rendering + `#GetVolume`
const GET_VOLUME_BODY = `<u:GetVolume xmlns:u="` + A_Prefix + A_Rendering + `"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetVolume>`

// Bass

const SET_BASS_ACTION = A_Prefix + A_Rendering + `#SetBass`
const SET_BASS_BODY_TEMPLATE = `<u:SetBass xmlns:u="` + A_Prefix + A_Rendering + `"><InstanceID>0</InstanceID><DesiredBass>{bass}</DesiredBass></u:SetBass>`
const SET_BASS_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetBassResponse xmlns:u="` + A_Prefix + A_Rendering + `"></u:SetBassResponse></s:Body></s:Envelope>`

const GET_BASS_ACTION = A_Prefix + A_Rendering + `#GetBass`
const GET_BASS_BODY = `<u:GetBass xmlns:u="` + A_Prefix + A_Rendering + `"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetBass>`

// Treble

const SET_TREBLE_ACTION = A_Prefix + A_Rendering + `#SetTreble`
const SET_TREBLE_BODY_TEMPLATE = `<u:SetTreble xmlns:u="` + A_Prefix + A_Rendering + `"><InstanceID>0</InstanceID><DesiredTreble>{treble}</DesiredTreble></u:SetTreble>`
const SET_TREBLE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetTrebleResponse xmlns:u="` + A_Prefix + A_Rendering + `"></u:SetTrebleResponse></s:Body></s:Envelope>`

const GET_TREBLE_ACTION = A_Prefix + A_Rendering + `#GetTreble`
const GET_TREBLE_BODY = `<u:GetTreble xmlns:u="` + A_Prefix + A_Rendering + `"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetTreble>`

// Loudness

const SET_LOUDNESS_ACTION = A_Prefix + A_Rendering + `#SetLoudness`
const SET_LOUDNESS_BODY_TEMPLATE = `<u:SetLoudness xmlns:u="` + A_Prefix + A_Rendering + `"><InstanceID>0</InstanceID><Channel>Master</Channel><DesiredLoudness>{loudness}</DesiredLoudness></u:SetLoudness>`
const SET_LOUDNESS_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetLoudnessResponse xmlns:u="` + A_Prefix + A_Rendering + `"></u:SetLoudnessResponse></s:Body></s:Envelope>`

const GET_LOUDNESS_ACTION = A_Prefix + A_Rendering + `#GetLoudness`
const GET_LOUDNESS_BODY = `<u:GetLoudness xmlns:u="` + A_Prefix + A_Rendering + `"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetLoudness>`

// Led State

const SET_LEDSTATE_ACTION = A_Prefix + A_Device + `#SetLEDState`
const SET_LEDSTATE_BODY_TEMPLATE = `<u:SetLEDState xmlns:u="` + A_Prefix + A_Device + `"><DesiredLEDState>{ledstate}</DesiredLEDState>`
const SET_LEDSTATE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetLEDStateResponse xmlns:u="` + A_Prefix + A_Device + `"></u:SetLEDStateResponse></s:Body></s:Envelope>`

const GET_LEDSTATE_ACTION = A_Prefix + A_Device + `#GetLEDState`
const GET_LEDSTATE_BODY = `<u:GetLEDState xmlns:u="` + A_Prefix + A_Device + `"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetLEDState>`

const SET_PLAYER_NAME_ACTION = A_Prefix + A_Device + `#SetZoneAttributes`
const SET_PLAYER_NAME_BODY_TEMPLATE = `"<u:SetZoneAttributes xmlns:u="` + A_Prefix + A_Device + `"><DesiredZoneName>{playername}</DesiredZoneName><DesiredIcon/><DesiredConfiguration/></u:SetZoneAttributes>`
const SET_PLAYER_NAME_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetZoneAttributesResponse xmlns:u="` + A_Prefix + A_Device + `"></u:SetZoneAttributesResponse></s:Body></s:Envelope>`

const GET_PLAYER_NAME_ACTION = A_Prefix + A_Device + `#GetZoneAttributes`
const GET_PLAYER_NAME_BODY = `<u:GetZoneAttributes xmlns:u="` + A_Prefix + A_Device + `"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetZoneAttributes>`

// Group

// const JOIN_ACTION = A_Prefix + A_Transport + `#SetAVTransportURI`
// const JOIN_BODY_TEMPLATE = `<u:SetAVTransportURI xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><CurrentURI>x-rincon:{master_uid}</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI>`
// const JOIN_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetAVTransportURIResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:SetAVTransportURIResponse></s:Body></s:Envelope>`

// const UNJOIN_ACTION = A_Prefix + A_Transport + `#BecomeCoordinatorOfStandaloneGroup`
// const UNJOIN_BODY = `<u:BecomeCoordinatorOfStandaloneGroup xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><Speed>1</Speed></u:BecomeCoordinatorOfStandaloneGroup>`
// const UNJOIN_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:BecomeCoordinatorOfStandaloneGroupResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:BecomeCoordinatorOfStandaloneGroupResponse></s:Body></s:Envelope>`

// Play Mode

// const SET_PLAYMODE_ACTION = A_Prefix + A_Transport + `#SetPlayMode`
// const SET_PLAYMODE_BODY_TEMPLATE = `<u:SetPlayMode xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><NewPlayMode>{playmode}</NewPlayMode></u:GetTransportSettings>`
// const SET_PLAYMODE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetPlayModeResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:SetPlayModeResponse></s:Body></s:Envelope>`

// const GET_PLAYMODE_ACTION = A_Prefix + A_Transport + `#GetTransportSettings`
// const GET_PLAYMODE_BODY = `<u:GetTransportSettings xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID></u:GetTransportSettings>`

// TODO: SetLineIn (Testing)

// const SET_LINEIN_ACTION = A_Prefix + A_Transport + `#SetAVTransportURI`
// const SET_LINEIN_BODY_TEMPLATE = `<u:SetAVTransportURI xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><CurrentURI>x-rincon-stream:{speaker_uid}</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI>`
// const SET_LINEIN_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetAVTransportURIResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:SetAVTransportURIResponse></s:Body></s:Envelope>`

// Current Track

// const GET_CUR_TRACK_ACTION = A_Prefix + A_Transport + `#GetPositionInfo`
// const GET_CUR_TRACK_BODY = `<u:GetPositionInfo xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetPositionInfo>`

// Que

// const PLAY_FROM_QUEUE_ACTION = A_Prefix + A_Transport + `#Seek`
// const PLAY_FROM_QUEUE_BODY_TEMPLATE = `<u:Seek xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><Unit>TRACK_NR</Unit><Target>{track}</Target></u:Seek>`
// const PLAY_FROM_QUEUE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SeekResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:SeekResponse></s:Body></s:Envelope>`

// TODO: AddToQue (Testing)

// const ADD_TO_QUEUE_ACTION = A_Prefix + `AVTransport:1#AddURIToQueue`
// const ADD_TO_QUEUE_BODY_TEMPLATE = `<u:AddURIToQueue xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><EnqueuedURI>{uri}</EnqueuedURI><EnqueuedURIMetaData></EnqueuedURIMetaData><DesiredFirstTrackNumberEnqueued>{index}</DesiredFirstTrackNumberEnqueued><EnqueueAsNext>{as_next}</EnqueueAsNext></u:AddURIToQueue>`
// const ADD_TO_QUEUE_RESPONSE = ``

// const REMOVE_FROM_QUEUE_ACTION = A_Prefix + `AVTransport:1#RemoveTrackFromQueue`
// const REMOVE_FROM_QUEUE_BODY_TEMPLATE = `<u:RemoveTrackFromQueue xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><ObjectID>Q:0/{track}</ObjectID><UpdateID>0</UpdateID></u:RemoveTrackFromQueue>`
// const REMOVE_FROM_QUEUE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:RemoveTrackFromQueueResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:RemoveTrackFromQueueResponse></s:Body></s:Envelope>`

// const CLEAR_QUEUE_ACTION = A_Prefix + A_Transport + `#RemoveAllTracksFromQueue`
// const CLEAR_QUEUE_BODY = `<u:RemoveAllTracksFromQueue xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID></u:RemoveAllTracksFromQueue>`
// const CLEAR_QUEUE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:RemoveAllTracksFromQueueResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:RemoveAllTracksFromQueueResponse></s:Body></s:Envelope>`

const GET_QUEUE_ACTION = A_Prefix + A_Content + `#Browse`
const GET_QUEUE_BODY_TEMPLATE = `<u:Browse xmlns:u="` + A_Prefix + A_Content + `"><ObjectID>Q:0</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>dc:title,res,dc:creator,upnp:artist,upnp:album,upnp:albumArtURI</Filter><StartingIndex>{start}</StartingIndex><RequestedCount>{count}</RequestedCount><SortCriteria></SortCriteria></u:Browse>`

// Favorites

const GET_FAVORITES_RADIO_STATIONS_ACTION = A_Prefix + A_Content + `#Browse`
const GET_FAVORITES_RADIO_STATIONS_BODY_TEMPLATE = `<u:Browse xmlns:u="` + A_Prefix + A_Content + `"><ObjectID>R:0/0</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter><StartingIndex>{start}</StartingIndex><RequestedCount>{count}</RequestedCount><SortCriteria></SortCriteria></u:Browse>`

const GET_FAVORITES_RADIO_SHOWS_ACTION = A_Prefix + A_Content + `#Browse`
const GET_FAVORITES_RADIO_SHOWS_BODY_TEMPLATE = `<u:Browse xmlns:u="` + A_Prefix + A_Content + `"><ObjectID>R:0/1</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter><StartingIndex>{start}</StartingIndex><RequestedCount>{count}</RequestedCount><SortCriteria></SortCriteria></u:Browse>`

const GET_FAVORITES_SONOS_ACTION = A_Prefix + A_Content + `#Browse`
const GET_FAVORITES_SONOS_BODY_TEMPLATE = `<u:Browse xmlns:u="` + A_Prefix + A_Content + `"><ObjectID>FV:2</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter><StartingIndex>{start}</StartingIndex><RequestedCount>{count}</RequestedCount><SortCriteria></SortCriteria></u:Browse>`

// TODO: PlayURI (Testing)

// const PLAY_URI_ACTION = A_Prefix + A_Transport + `#SetAVTransportURI`
// const PLAY_URI_BODY_TEMPLATE = `<u:SetAVTransportURI xmlns:u="` + A_Prefix + A_Transport + `"><InstanceID>0</InstanceID><CurrentURI>{uri}</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI>`
// const PLAY_URI_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetAVTransportURIResponse xmlns:u="` + A_Prefix + A_Transport + `"></u:SetAVTransportURIResponse></s:Body></s:Envelope>`
