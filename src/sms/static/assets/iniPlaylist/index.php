<!DOCTYPE html>
<html>
<head>
	<title></title>
	<link rel="stylesheet" type="text/css" href="iniaudioplaylist.css">
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
</head>
<body>

<div class="item__play__box" id="plybox1">
    <div class="item__header">
    	<div class="playing">
	    	<span class="npAction">
	    			Now Playing...
	    	</span>
	    	<span class="npTitle">
	    		sffsfs
	    	</span>
	    </div>

		<audio preload id="audio1" controls="controls" src="a.mp3" type="audio/amr">Your browser does not support HTML5 Audio!</audio>
    </div>

    <ul class="item__playlist" id="playlist1">
    	<li class="active">
    		<div class="playlist__item" onclick="audioPlaylist(this, 'plybox1', 'a.mp3', 'audio1', 'playlist1');">
    			<div class="item__sl">1.</div>
    			<div class="item__title">Golmaal Title Track - Songs.pk - 128Kbps</div>
    			<div class="item__length">2:46</div>
    		</div>
    	</li>
    	<li>
    		<div class="playlist__item" onclick="audioPlaylist(this, 'plybox1', 'b.mp3', 'audio1', 'playlist1');">
    			<div class="item__sl">1.</div>
    			<div class="item__title">Hum Nahi Sudhrenge - Songs.pk - 128Kbps</div>
    			<div class="item__length">2:46</div>
    		</div>
    	</li>
    </ul>

</div>




<!-- <iframe width="420" height="315"
src="http://localhost/iniAudioPlaylist/c.flv">
</iframe>  -->


<div class="item__play__box" id="plybox2">
    <div class="item__header">
		<video preload id="video1" controls="controls"
		  src="a.mp4" type="video/mp4">
			Your browser does not support the video tag.
		</video>
    </div>

    <ul class="item__playlist" id="playlist2">
    	<li class="active">
    		<div class="playlist__item" onclick="videoPlaylist(this, 'plybox2', 'a.mp4', 'video1', 'playlist2');">
    			<div class="item__sl">1.</div>
    			<div class="item__title">ANT MAN 2 Teaser pipra bidda onnek boro aro boro borao lagbe ar koto boro dibi</div>
    			<div class="item__length">2:46</div>
    		</div>
    	</li>
    	<li class="">
    		<div class="playlist__item" onclick="videoPlaylist(this, 'plybox2', 'b.mp4', 'video1', 'playlist2');">
    			<div class="item__sl">2.</div>
    			<div class="item__title">Ittefaq  Trailer</div>
    			<div class="item__length">2:46</div>
    		</div>
    	</li>
    </ul>
</div>

<script>
	function audioPlaylist(ele, playBox, track, playerID, playlistID) {
		$('#' + playerID).attr('src', track);
		document.getElementById(playerID).play();
		$('#' + playlistID).find('li.active').removeClass('active');
		$(ele).parent().addClass('active');	
		var trackName = $(ele).find('div.item__title').text();
		$('#'+playBox).find('span.npTitle').text(trackName);
	}


	function videoPlaylist(ele, playBox, track, playerID, playlistID) {
		$('#' + playerID).attr('src', track);
		// $(playerID).play();
		document.getElementById(playerID).play();
		$('#' + playlistID).find('li.active').removeClass('active');
		$(ele).parent().addClass('active');	
	}
</script>

</body>
</html>