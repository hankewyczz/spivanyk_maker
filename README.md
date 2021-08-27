A songbook generator for Ukrainian song-books. 

The songs must be saved locally to the `/songs` directory, using the ChordPro format. Songs are saved using the `.cho` extension. 

If you don't have the song downloaded locally, the program will prompt you to chose to download from WikiSpiv. The program can download and parse the WikiSpiv entry to fit the ChordProd format we need. 

The `main()` method takes a list of sections. Each section has a name, a list of song names, and tells us if we should sort the songs alphabetically or keep the given order.

That method generates a songbook with those sections, including an index (with alternate titles) and a chords page, containing all of the chords found in the songs. 


The default settings are contained in `consts.py`. This includes page sizes, margins, fonts, etc.