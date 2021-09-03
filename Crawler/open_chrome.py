import os 
def init_chrome():
    os.system("gnome-terminal -- sh -c 'google-chrome --remote-debugging-port=9222 --user-data-dir='~/workspace/test/knowledge_based_sentiment_analysis_community_crawler/ChromeProfile'; exec bash'")
init_chrome()