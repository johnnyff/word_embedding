import os 
def init_chrome():
    os.system("sudo -u wongi google-chrome --no-sandbox --remote-debugging-port=9222 --user-data-dir='~/workspace/test/knowledge_based_sentiment_analysis_community_crawler/ChromeProfile'")
    # os.system("gnome-terminal -- sh -c 'google-chrome --no-sandbox --remote-debugging-port=9222 --user-data-dir='~/workspace/test/knowledge_based_sentiment_analysis_community_crawler/ChromeProfile'; exec bash'")
init_chrome()