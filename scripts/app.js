(function(){
  var synth=window.speechSynthesis;
  if(!synth)return;
  var voiceSel=document.getElementById('tts-voice');
  var rateSlider=document.getElementById('tts-rate');
  var rateValEl=document.getElementById('tts-rate-val');
  var seekSlider=document.getElementById('tts-seek');
  var timeCurEl=document.getElementById('tts-time-cur');
  var timeTotalEl=document.getElementById('tts-time-total');
  var WPM=102;
  function fmtTime(secs){secs=Math.max(0,Math.round(secs));return Math.floor(secs/60)+':'+(secs%60<10?'0':'')+secs%60;}
  function idxToSecs(idx){return idx/(WPM*parseFloat(rateSlider.value)/60);}
  var ttsBar=document.getElementById('tts-bar');
  var skipBackBtn=document.getElementById('tts-skip-back');
  var playPauseBtn=document.getElementById('tts-playpause');
  var skipFwdBtn=document.getElementById('tts-skip-fwd');
  var sectionNameEl=document.getElementById('tts-section-name');
  if(!ttsBar)return;
  var voices=[];
  var wordSpans=[];
  var charOffsets=[];
  var rawText='';
  var currentIdx=0;
  var isSpeaking=false;
  var isPaused=false;
  var currentContentEl=null;
  var currentReadingEl=null;
  var currentSavedHtml=null;
  var userScrolled=false;
  var scrollLock=false;
  window.addEventListener('scroll',function(){if(!scrollLock)userScrolled=true;},{passive:true});
  function loadVoices(){
    voices=synth.getVoices();
    if(!voices.length)return;
    voiceSel.innerHTML='';
    var hu=voices.filter(function(v){return v.lang.startsWith('hu');});
    var list=hu.length?hu:voices;
    list.forEach(function(v){
      var o=document.createElement('option');
      o.value=voices.indexOf(v);
      o.textContent=v.name+' ('+v.lang+')'+(v.localService?' ♦':'');
      voiceSel.appendChild(o);
    });
  }
  loadVoices();
  if(synth.onvoiceschanged!==undefined)synth.onvoiceschanged=loadVoices;
  rateSlider.addEventListener('input',function(){
    rateValEl.textContent=parseFloat(rateSlider.value).toFixed(1)+'×';
    if(isSpeaking||isPaused){isSpeaking=false;isPaused=false;speakFrom(currentIdx);}
  });
  function buildSpansInPlace(el){
    currentSavedHtml=el.innerHTML;rawText='';wordSpans=[];charOffsets=[];
    function walk(node){
      if(node.nodeType===3){
        var frag=document.createDocumentFragment();
        node.textContent.split(/(\s+)/).forEach(function(tok){
          if(tok==='')return;
          if(/^\s+$/.test(tok)){
            if(rawText.length&&rawText[rawText.length-1]!==' ')rawText+=' ';
            frag.appendChild(document.createTextNode(tok));
          }else{
            charOffsets.push(rawText.length);rawText+=tok;
            var sp=document.createElement('span');
            sp.className='tts-word';sp.textContent=tok;sp.dataset.idx=wordSpans.length;
            sp.addEventListener('click',onWordClick);
            wordSpans.push(sp);frag.appendChild(sp);
          }
        });
        node.parentNode.replaceChild(frag,node);
      }else if(node.nodeType===1&&node.tagName!=='SCRIPT'&&node.tagName!=='STYLE'&&node.tagName!=='BUTTON'){
        Array.from(node.childNodes).forEach(walk);
      }
    }
    walk(el);
  }
  function markWord(idx){
    idx=Math.max(0,Math.min(idx,wordSpans.length-1));
    wordSpans.forEach(function(s,i){
      s.className='tts-word'+(i<idx?' done':i===idx?' current':'');
    });
    if(wordSpans[idx]&&!userScrolled){scrollLock=true;wordSpans[idx].scrollIntoView({block:'nearest',behavior:'smooth'});setTimeout(function(){scrollLock=false;},300);}
    currentIdx=idx;
    var total=wordSpans.length;
    seekSlider.max=total-1;seekSlider.value=idx;
    timeCurEl.textContent=fmtTime(idxToSecs(idx));
    timeTotalEl.textContent=fmtTime(idxToSecs(total-1));
  }
  function speakFrom(idx){
    userScrolled=false;
    if(synth.speaking||isPaused)synth.cancel();
    idx=Math.max(0,Math.min(idx,wordSpans.length-1));
    currentIdx=idx;
    var startChar=charOffsets[idx];
    var subText=rawText.slice(startChar);
    var utt=new SpeechSynthesisUtterance(subText);
    var selIdx=parseInt(voiceSel.value);
    if(!isNaN(selIdx)&&voices[selIdx])utt.voice=voices[selIdx];
    utt.lang='hu-HU';
    utt.rate=parseFloat(rateSlider.value);utt.pitch=1;
    utt.onstart=function(){isSpeaking=true;isPaused=false;setUI('speaking');markWord(idx);};
    utt.onboundary=function(e){
      if(e.name!=='word')return;
      var absChar=startChar+e.charIndex;
      var found=wordSpans.length-1;
      for(var i=0;i<charOffsets.length;i++){
        if(charOffsets[i]<=absChar&&(i+1>=charOffsets.length||charOffsets[i+1]>absChar)){found=i;break;}
      }
      markWord(found);
    };
    utt.onend=function(){
      if(!isSpeaking)return;
      isSpeaking=false;isPaused=false;
      wordSpans.forEach(function(s){s.className='tts-word done';});
      var total=wordSpans.length;
      seekSlider.max=total-1;seekSlider.value=total-1;
      timeCurEl.textContent=fmtTime(idxToSecs(total-1));
      timeTotalEl.textContent=fmtTime(idxToSecs(total-1));
      setUI('done');
    };
    utt.onerror=function(e){if(e.error==='interrupted'||e.error==='canceled')return;};
    synth.speak(utt);
  }
  function onWordClick(e){
    if(!isSpeaking&&!isPaused)return;
    var idx=parseInt(e.currentTarget.dataset.idx);
    isSpeaking=false;isPaused=false;speakFrom(idx);
  }
  var SVG_PLAY='<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>';
  var SVG_PAUSE='<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>';
  var SVG_RESTART='<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4"/></svg>';
  function setUI(state){
    var canSkip=state==='speaking'||state==='paused';
    skipBackBtn.disabled=!canSkip;
    skipFwdBtn.disabled=!canSkip;
    if(state==='speaking'){
      playPauseBtn.disabled=false;
      playPauseBtn.innerHTML=SVG_PAUSE;
      playPauseBtn.title='Szünet';
    }else if(state==='paused'){
      playPauseBtn.disabled=false;
      playPauseBtn.innerHTML=SVG_PLAY;
      playPauseBtn.title='Folytatás';
    }else if(state==='done'){
      playPauseBtn.disabled=false;
      playPauseBtn.innerHTML=SVG_RESTART;
      playPauseBtn.title='Újraindítás';
    }else{
      playPauseBtn.disabled=true;
      playPauseBtn.innerHTML=SVG_PLAY;
      playPauseBtn.title='Lejátszás';
    }
  }
  function doSkip(delta){
    if(!isSpeaking&&!isPaused)return;
    var next=Math.max(0,Math.min(currentIdx+delta,wordSpans.length-1));
    isSpeaking=false;isPaused=false;speakFrom(next);
  }
  function restoreContent(){
    if(currentContentEl&&currentSavedHtml!==null){
      currentContentEl.innerHTML=currentSavedHtml;
      currentSavedHtml=null;
    }
  }
  function stopAll(){
    isSpeaking=false;isPaused=false;
    synth.cancel();
    restoreContent();
    ttsBar.hidden=true;
    wordSpans=[];charOffsets=[];
    seekSlider.value=0;seekSlider.max=100;
    timeCurEl.textContent='0:00';timeTotalEl.textContent='0:00';
    setUI('idle');
  }
  document.querySelectorAll('.tts-btn').forEach(function(btn){
    btn.addEventListener('click',function(e){
      e.stopPropagation();e.preventDefault();
      var contentId=btn.dataset.ttsContent;
      var readingId=btn.dataset.ttsReading;
      var detailsId=btn.dataset.ttsDetails;
      var label=btn.dataset.ttsLabel||'';
      var contentEl=document.getElementById(contentId);
      var readingEl=document.getElementById(readingId);
      if(!contentEl)return;
      if(detailsId){var det=document.getElementById(detailsId);if(det)det.open=true;}
      if(isSpeaking||isPaused){synth.cancel();restoreContent();}
      isSpeaking=false;isPaused=false;
      currentContentEl=contentEl;currentReadingEl=readingEl;
      buildSpansInPlace(contentEl);
      if(!wordSpans.length)return;
      sectionNameEl.textContent=label;
      ttsBar.hidden=false;
      speakFrom(0);
    });
  });
  skipBackBtn.addEventListener('click',function(){doSkip(-5);});
  skipFwdBtn.addEventListener('click',function(){doSkip(5);});
  playPauseBtn.addEventListener('click',function(){
    if(isSpeaking){synth.pause();isPaused=true;isSpeaking=false;setUI('paused');}
    else if(isPaused){synth.resume();isPaused=false;isSpeaking=true;setUI('speaking');}
    else if(wordSpans.length){isSpeaking=false;isPaused=false;speakFrom(0);}
  });
  seekSlider.addEventListener('input',function(){
    var idx=parseInt(seekSlider.value);
    timeCurEl.textContent=fmtTime(idxToSecs(idx));
  });
  seekSlider.addEventListener('change',function(){
    var idx=parseInt(seekSlider.value);
    if(wordSpans.length){isSpeaking=false;isPaused=false;speakFrom(idx);}
  });
  document.getElementById('tts-close').addEventListener('click',stopAll);
  window.addEventListener('pagehide',function(){synth.cancel();});
  setUI('idle');
})();
