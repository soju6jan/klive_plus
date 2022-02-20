from .basic import *
    
class SourceNaverSports(SourceBase):
    name = '네이버 스포츠'
    source_name = 'naver_sports'
    
    def get_list(self):
        url = 'https://sports.news.naver.com/index'
        text = requests.get(url, headers=default_headers).text
        tmp = text.split("liveBoxList\":")
        if len(tmp) == 1:
            return
        text = text.split("liveBoxList\":")[1].splitlines()[0].strip(', ')
        data = json.loads(text)
        self.reset_ch_list()
        for item in data:
            url = f"https://api-gw.sports.naver.com/schedule/{item['gameId']}/lives"
            game_data = requests.get(url, headers=default_headers).json()
            if game_data['code'] == 404:
                continue
            for tmp in game_data['result']['lives']:
                self.ch_list[str(tmp['liveId'])] = Channel(tmp['liveId'], tmp['streamTitle'], f"[{item['categoryName']}] {item['title']}")
        return self.ch_list

    def get_url(self, ch_id):
        url = f'https://proxy-gateway.sports.naver.com/livecloud/lives/{ch_id}/playback?countryCode=KR&devt=HTML5_PC&timeMachine=true&p2p=true&includeThumbnail=true&pollingStatus=true#'
        data = requests.get(url, headers=default_headers).json()
        url = data['media'][0]['path']
        return url
