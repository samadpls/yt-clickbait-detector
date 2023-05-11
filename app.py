import streamlit as st
import time
import json
import urllib.request
import re
from scipy.spatial import distance
from sentence_transformers import SentenceTransformer
from youtube_transcript_api import YouTubeTranscriptApi


@st.cache(allow_output_mutation=True,suppress_st_warning = True)
def checking(search):
    with st.spinner("Fetching results..."):
        def loading():
            return SentenceTransformer('distilbert-base-nli-mean-tokens')
    
    model =loading() 

    output,urls,ten=[],[],0
    progresss=st.progress(0)
    
    html= urllib.request.urlopen(f"https://www.youtube.com/results?search_query={search}")
    videos=list(set(re.findall("watch\?v=(\S{11})",html.read().decode())))
    for video_id in videos[:10]:
            ten+=10
            progresss.progress(ten)
            
            url = f"https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v={video_id}"
            try:
                with urllib.request.urlopen(url) as response:
                    response_text = response.read()
                    data = json.loads(response_text.decode())
            except urllib.error.URLError:
                st.error('Unable to connect to the internet. Please check your connection.')
                return

            try:
                caption = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                output.append(data['title'].lower())
                output.append(" ".join(caption[i]['text'] for i in range(len(caption))).lower())
                urls.append(video_id)

            except Exception as e:
                pass
   
    if output:
        similarities = []
        for sentence in range(0, len(output), 2):
            sentence_embeddings = model.encode([output[sentence], output[sentence+1]])
            value = 1 - distance.cosine(sentence_embeddings[0], sentence_embeddings[1])
            similarities.append(value)

        return [urls[index] for index in range(len(similarities)) if similarities[index] > 0.5]
   
    else:
        st.error('Unable to find videos in English', icon="😔")


def main():
    st.set_page_config(page_title="YT-ClickBait Detector", page_icon='images/youtube.png')

    with open('styles.css') as f:
        st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)
        
    st.markdown("""<a href='https://github.com/samadpls/yt-clickbait-detector'><img src='https://img.shields.io/github/stars/samadpls/yt-clickbait-detector?color=red&label=star%20me&logoColor=red&style=social'></a>""",unsafe_allow_html=True)    
    img , heading =  st.columns([1,5])
    with img:
        st.image('images/youtube.png', width=90)
    with heading:
        st.markdown('# YouTube ClickBait Detector')
    
    search=st.text_input("Search Video ", '')
    st.markdown("```It only works on Videos having English captions.```")
    if search:
        valid_urls= checking(search.strip().replace(' ', '+'))
        if valid_urls:
                for i, valid_url in enumerate(valid_urls[:3]):
                    st.components.v1.iframe(src=f"https://www.youtube.com/embed/{valid_url}", height=300)

       
        else:
            st.error('Sorry! could not able to find a valid video', icon="😔")
    

if __name__=="__main__":
    main()
