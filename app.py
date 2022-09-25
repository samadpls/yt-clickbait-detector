import streamlit as st
import time
import json
import urllib.request
import re
from scipy.spatial import distance
from sentence_transformers import SentenceTransformer
from youtube_transcript_api import YouTubeTranscriptApi

st.set_page_config(page_title="YT-ClickBait Detector", page_icon='images/youtube.png')
@st.cache(allow_output_mutation=True,suppress_st_warning = True)
def loading():   
    return SentenceTransformer('distilbert-base-nli-mean-tokens')
   
        
def checking(search):
    
    model =loading() 

    output,urls,ten=[],[],0
    progresss=st.progress(0)
    
    html= urllib.request.urlopen(f"https://www.youtube.com/results?search_query={search}")
    videos=list(set(re.findall("watch\?v=(\S{11})",html.read().decode())))
    for  VideoID in videos[:10]:
        params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % VideoID}
        url = "https://www.youtube.com/oembed"
        query_string = urllib.parse.urlencode(params)
        url = url + "?" + query_string
        ten+=10
        progresss.progress(ten)
        

       
        try:
            with urllib.request.urlopen(url) as response:
                response_text = response.read()
                data = json.loads(response_text.decode())
        except:
            st.info("Refresh your browser")
        
        try:
            caption = YouTubeTranscriptApi.get_transcript(VideoID,languages=['en'])
            # print(data['title'])
            output.append(data['title'].lower())
            output.append(" ".join(caption[i]['text'] for i in range(len(caption))).lower())
            urls.append(VideoID)
        
        except Exception as e:
            pass
    if output:
        result=[]
        for sentence in range(0,len(output),2):
            sentence_embeddings = model.encode([output[sentence],output[sentence+1]])
            value= 1 - distance.cosine(sentence_embeddings[0], sentence_embeddings[1])
            result.append(value)
            
            # print(result)
        valid=[urls[index] for index in range(len( result)) if result[index] >0.5]
        if valid:
            if len(valid)>=3:
                st.components.v1.iframe(src=f"https://www.youtube.com/embed/{valid[0]}", height=300)
                st.components.v1.iframe(src=f"https://www.youtube.com/embed/{valid[1]}", height=300)
                st.components.v1.iframe(src=f"https://www.youtube.com/embed/{valid[2]}", height=300)
                st.success("made with 🤍 by samadpls")
            elif len(valid)==2:
                st.components.v1.iframe(src=f"https://www.youtube.com/embed/{valid[0]}", height=300)
                st.components.v1.iframe(src=f"https://www.youtube.com/embed/{valid[1]}", height=300)
                st.success("made with 🤍 by samadpls")  
            else:
                st.components.v1.iframe(src=f"https://www.youtube.com/embed/{valid[0]}", height=300) 
                st.success("made with 🤍 by samadpls")     
        else:
            st.error('Sorry! could not able to find a valid video', icon="😔")
    else:
        st.error('Unable to find videos in English', icon="😔")


def main():
    with open('styles.css') as f:
        st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)
        
    st.markdown("""<div><h3><a  style="color:#FFFFFF" href="https://github.com/samadpls/yt-clickbait-detector">star it</a> ⭐</h3></div>""",unsafe_allow_html=True)   
    
    img , heading =  st.columns([1,5])
    with img:
        st.image('images/youtube.png', width=90)
    with heading:
        st.markdown('# YouTube ClickBait Detector')
    
    search=st.text_input("Search Video ", '')
    st.markdown("```It only works on Videos having English captions.```")
    if search:
        checking(search.strip().replace(' ', '+'))
    

if __name__=="__main__":
    main()