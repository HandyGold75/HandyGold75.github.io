package Gonos

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

// TODO
const A_Prefix = `"urn:schemas-upnp-org:service:`
const A_Transport = `AVTransport:1#`
const A_Rendering = `RenderingControl:1#`
const A_Device = `DeviceProperties:1#`
const A_Content = `ContentDirectory:1#`
const A_Posfix = `"`

// State

// Change??? -> const GET_CUR_TRANSPORT_ACTION = `"urn:schemas-upnp-org:service:AVTransport:1#GetTransportInfo` + A_Posfix
const GET_CUR_TRANSPORT_ACTION = `"urn:schema-upnp-org:service:AVTransport:1#GetTransportInfo` + A_Posfix
const GET_CUR_TRANSPORT_BODY = `<u:GetTransportInfo xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:GetTransportInfo></s:Body></s:Envelope>`

// Play

const PLAY_ACTION = A_Prefix + A_Transport + `Play` + A_Posfix
const PLAY_BODY = `<u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Play>`
const PLAY_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:PlayResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:PlayResponse></s:Body></s:Envelope>`

// Pause

const PAUSE_ACTION = A_Prefix + A_Transport + `Pause` + A_Posfix
const PAUSE_BODY = `<u:Pause xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Pause>`
const PAUSE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:PauseResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:PauseResponse></s:Body></s:Envelope>`

// Stop

const STOP_ACTION = A_Prefix + A_Transport + `Stop` + A_Posfix
const STOP_BODY = `<u:Stop xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Stop>`
const STOP_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:StopResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:StopResponse></s:Body></s:Envelope>`

// Next

const NEXT_ACTION = A_Prefix + A_Transport + `Next` + A_Posfix
const NEXT_BODY = `<u:Next xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Next>`
const NEXT_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:NextResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:NextResponse></s:Body></s:Envelope>`

// Previous

const PREV_ACTION = A_Prefix + A_Transport + `Previous` + A_Posfix
const PREV_BODY = `<u:Previous xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Previous>`
const PREV_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:PreviousResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:PreviousResponse></s:Body></s:Envelope>`

// Seek

const SEEK_ACTION = A_Prefix + A_Transport + `Seek` + A_Posfix
const SEEK_BODY_TEMPLATE = `<u:Seek xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Unit>REL_TIME</Unit><Target>{timestamp}</Target></u:Seek>`
const SEEK_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SeekResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:SeekResponse></s:Body></s:Envelope>`

// Mute

const SET_MUTE_ACTION = A_Prefix + A_Rendering + `SetMute` + A_Posfix
const SET_MUTE_BODY_TEMPLATE = `<u:SetMute xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel><DesiredMute>{mute}</DesiredMute></u:SetMute>`
const SET_MUTE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetMuteResponse xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"></u:SetMuteResponse></s:Body></s:Envelope>`

const GET_MUTE_ACTION = A_Prefix + A_Rendering + `GetMute` + A_Posfix
const GET_MUTE_BODY = `<u:GetMute xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetMute>`

// Volume

const SET_VOLUME_ACTION = A_Prefix + A_Rendering + `SetVolume` + A_Posfix
const SET_VOLUME_BODY_TEMPLATE = `<u:SetVolume xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel><DesiredVolume>{volume}</DesiredVolume></u:SetVolume>`
const SET_VOLUME_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetVolumeResponse xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"></u:SetVolumeResponse></s:Body></s:Envelope>`

const GET_VOLUME_ACTION = A_Prefix + A_Rendering + `GetVolume` + A_Posfix
const GET_VOLUME_BODY = `<u:GetVolume xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetVolume>`

// Bass

const SET_BASS_ACTION = A_Prefix + A_Rendering + `SetBass` + A_Posfix
const SET_BASS_BODY_TEMPLATE = `<u:SetBass xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><DesiredBass>{bass}</DesiredBass></u:SetBass>`
const SET_BASS_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetBassResponse xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"></u:SetBassResponse></s:Body></s:Envelope>`

const GET_BASS_ACTION = A_Prefix + A_Rendering + `GetBass` + A_Posfix
const GET_BASS_BODY = `<u:GetBass xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetBass>`

// Treble

const SET_TREBLE_ACTION = A_Prefix + A_Rendering + `SetTreble` + A_Posfix
const SET_TREBLE_BODY_TEMPLATE = `<u:SetTreble xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><DesiredTreble>{treble}</DesiredTreble></u:SetTreble>`
const SET_TREBLE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetTrebleResponse xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"></u:SetTrebleResponse></s:Body></s:Envelope>`

const GET_TREBLE_ACTION = A_Prefix + A_Rendering + `GetTreble` + A_Posfix
const GET_TREBLE_BODY = `<u:GetTreble xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetTreble>`

// Loudness

const SET_LOUDNESS_ACTION = A_Prefix + A_Rendering + `SetLoudness` + A_Posfix
const SET_LOUDNESS_BODY_TEMPLATE = `<u:SetLoudness xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel><DesiredLoudness>{loudness}</DesiredLoudness></u:SetLoudness>`
const SET_LOUDNESS_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetLoudnessResponse xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"></u:SetLoudnessResponse></s:Body></s:Envelope>`

const GET_LOUDNESS_ACTION = A_Prefix + A_Rendering + `GetLoudness` + A_Posfix
const GET_LOUDNESS_BODY = `<u:GetLoudness xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetLoudness>`

// Led State

const SET_LEDSTATE_ACTION = A_Prefix + A_Device + `SetLEDState` + A_Posfix
const SET_LEDSTATE_BODY_TEMPLATE = `<u:SetLEDState xmlns:u="urn:schemas-upnp-org:service:DeviceProperties:1"><DesiredLEDState>{ledstate}</DesiredLEDState>`
const SET_LEDSTATE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetLEDStateResponse xmlns:u="urn:schemas-upnp-org:service:DeviceProperties:1"></u:SetLEDStateResponse></s:Body></s:Envelope>`

const GET_LEDSTATE_ACTION = A_Prefix + A_Device + `GetLEDState` + A_Posfix
const GET_LEDSTATE_BODY = `<u:GetLEDState xmlns:u="urn:schemas-upnp-org:service:DeviceProperties:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetLEDState>`

const SET_PLAYER_NAME_ACTION = A_Prefix + A_Device + `SetZoneAttributes` + A_Posfix
const SET_PLAYER_NAME_BODY_TEMPLATE = `"<u:SetZoneAttributes xmlns:u="urn:schemas-upnp-org:service:DeviceProperties:1"><DesiredZoneName>{playername}</DesiredZoneName><DesiredIcon/><DesiredConfiguration/></u:SetZoneAttributes>` + A_Posfix
const SET_PLAYER_NAME_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetZoneAttributesResponse xmlns:u="urn:schemas-upnp-org:service:DeviceProperties:1"></u:SetZoneAttributesResponse></s:Body></s:Envelope>`

const GET_PLAYER_NAME_ACTION = A_Prefix + A_Device + `GetZoneAttributes` + A_Posfix
const GET_PLAYER_NAME_BODY = `<u:GetZoneAttributes xmlns:u="urn:schemas-upnp-org:service:DeviceProperties:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetZoneAttributes>`

// Group

const JOIN_ACTION = A_Prefix + A_Transport + `SetAVTransportURI` + A_Posfix
const JOIN_BODY_TEMPLATE = `<u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>x-rincon:{master_uid}</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI>`
const JOIN_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetAVTransportURIResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:SetAVTransportURIResponse></s:Body></s:Envelope>`

const UNJOIN_ACTION = A_Prefix + A_Transport + `BecomeCoordinatorOfStandaloneGroup` + A_Posfix
const UNJOIN_BODY = `<u:BecomeCoordinatorOfStandaloneGroup xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:BecomeCoordinatorOfStandaloneGroup>`
const UNJOIN_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:BecomeCoordinatorOfStandaloneGroupResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:BecomeCoordinatorOfStandaloneGroupResponse></s:Body></s:Envelope>`

// Play Mode

const SET_PLAYMODE_ACTION = A_Prefix + A_Transport + `SetPlayMode` + A_Posfix
const SET_PLAYMODE_BODY_TEMPLATE = `<u:SetPlayMode xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><NewPlayMode>{playmode}</NewPlayMode></u:GetTransportSettings>`
const SET_PLAYMODE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetPlayModeResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:SetPlayModeResponse></s:Body></s:Envelope>`

const GET_PLAYMODE_ACTION = A_Prefix + A_Transport + `GetTransportSettings` + A_Posfix
const GET_PLAYMODE_BODY = `<u:GetTransportSettings xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:GetTransportSettings>`

// TODO: SetLineIn (Testing)

const SET_LINEIN_ACTION = A_Prefix + A_Transport + `SetAVTransportURI` + A_Posfix
const SET_LINEIN_BODY_TEMPLATE = `<u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>x-rincon-stream:{speaker_uid}</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI>`
const SET_LINEIN_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetAVTransportURIResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:SetAVTransportURIResponse></s:Body></s:Envelope>`

// Current Track

const GET_CUR_TRACK_ACTION = A_Prefix + A_Transport + `GetPositionInfo` + A_Posfix
const GET_CUR_TRACK_BODY = `<u:GetPositionInfo xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Channel>Master</Channel></u:GetPositionInfo>`

// Que

const PLAY_FROM_QUEUE_ACTION = A_Prefix + A_Transport + `Seek` + A_Posfix
const PLAY_FROM_QUEUE_BODY_TEMPLATE = `<u:Seek xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Unit>TRACK_NR</Unit><Target>{track}</Target></u:Seek>`
const PLAY_FROM_QUEUE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SeekResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:SeekResponse></s:Body></s:Envelope>`

// TODO: AddToQue (Testing)
// Change with quoates?????
const ADD_TO_QUEUE_ACTION = `urn:schemas-upnp-org:service:AVTransport:1#AddURIToQueue`
const ADD_TO_QUEUE_BODY_TEMPLATE = `<u:AddURIToQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><EnqueuedURI>{uri}</EnqueuedURI><EnqueuedURIMetaData></EnqueuedURIMetaData><DesiredFirstTrackNumberEnqueued>{index}</DesiredFirstTrackNumberEnqueued><EnqueueAsNext>{as_next}</EnqueueAsNext></u:AddURIToQueue>`
const ADD_TO_QUEUE_RESPONSE = ``

const REMOVE_FROM_QUEUE_ACTION = `urn:schemas-upnp-org:service:AVTransport:1#RemoveTrackFromQueue`
const REMOVE_FROM_QUEUE_BODY_TEMPLATE = `<u:RemoveTrackFromQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><ObjectID>Q:0/{track}</ObjectID><UpdateID>0</UpdateID></u:RemoveTrackFromQueue>`
const REMOVE_FROM_QUEUE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:RemoveTrackFromQueueResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:RemoveTrackFromQueueResponse></s:Body></s:Envelope>`

const CLEAR_QUEUE_ACTION = A_Prefix + A_Transport + `RemoveAllTracksFromQueue` + A_Posfix
const CLEAR_QUEUE_BODY = `<u:RemoveAllTracksFromQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:RemoveAllTracksFromQueue>`
const CLEAR_QUEUE_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:RemoveAllTracksFromQueueResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:RemoveAllTracksFromQueueResponse></s:Body></s:Envelope>`

const GET_QUEUE_ACTION = A_Prefix + A_Content + `Browse` + A_Posfix
const GET_QUEUE_BODY_TEMPLATE = `<u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1"><ObjectID>Q:0</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>dc:title,res,dc:creator,upnp:artist,upnp:album,upnp:albumArtURI</Filter><StartingIndex>{start}</StartingIndex><RequestedCount>{count}</RequestedCount><SortCriteria></SortCriteria></u:Browse>`

// Favorites

const GET_FAVORITES_RADIO_STATIONS_ACTION = A_Prefix + A_Content + `Browse` + A_Posfix
const GET_FAVORITES_RADIO_STATIONS_BODY_TEMPLATE = `<u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1"><ObjectID>R:0/0</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter><StartingIndex>{start}</StartingIndex><RequestedCount>{count}</RequestedCount><SortCriteria></SortCriteria></u:Browse>`

const GET_FAVORITES_RADIO_SHOWS_ACTION = A_Prefix + A_Content + `Browse` + A_Posfix
const GET_FAVORITES_RADIO_SHOWS_BODY_TEMPLATE = `<u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1"><ObjectID>R:0/1</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter><StartingIndex>{start}</StartingIndex><RequestedCount>{count}</RequestedCount><SortCriteria></SortCriteria></u:Browse>`

const GET_FAVORITES_SONOS_ACTION = A_Prefix + A_Content + `Browse` + A_Posfix
const GET_FAVORITES_SONOS_BODY_TEMPLATE = `<u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1"><ObjectID>FV:2</ObjectID><BrowseFlag>BrowseDirectChildren</BrowseFlag><Filter>*</Filter><StartingIndex>{start}</StartingIndex><RequestedCount>{count}</RequestedCount><SortCriteria></SortCriteria></u:Browse>`

// TODO: PlayURI (Testing)

const PLAY_URI_ACTION = A_Prefix + A_Transport + `SetAVTransportURI` + A_Posfix
const PLAY_URI_BODY_TEMPLATE = `<u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>{uri}</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI>`
const PLAY_URI_RESPONSE = `<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetAVTransportURIResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:SetAVTransportURIResponse></s:Body></s:Envelope>`
