module HG75

go 1.24.5

require (
	github.com/HandyGold75/GOLib/cfg v0.0.0-20250724140744-ffdd0424f7ed
	github.com/HandyGold75/GOLib/logger v0.0.0-20250724140744-ffdd0424f7ed
	github.com/HandyGold75/GOLib/scheduler v0.0.0-20250724140744-ffdd0424f7ed
	github.com/achetronic/tapogo v0.2.0
	golang.org/x/term v0.33.0
)

replace github.com/HandyGold75/GOLib/logger => ../../GOLib/logger/

require golang.org/x/sys v0.34.0 // indirect
