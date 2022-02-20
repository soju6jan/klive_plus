from .basic import *
import gzip

class SourceSSTV(SourceBase):
    name = '삼성TV+'
    source_name = 'sstv'
    def get_list(self):
        self.reset_ch_list()
        data = json.loads(gzip.decompress(requests.get(DATA_URL).content))['regions']
        regions = [('kr', '한국'), ('us', '미국'), ('gb', '영국'), ('in', '인도'), ('de', '독일'), ('it', '이탈리아'), ('es', '스페인'), ('fr', '프랑스'), ('fr', '프랑스'), ('ch', '스위스'), ('at', '오스트리아')]
        if ModelSetting.get_bool(f'base_sstv_only_kor'):
            regions = [regions[0]]
        
        for code, country in regions:
            for channel, value in data[code]['channels'].items():
                if '[SEASON_TITLE]' in value['url']:
                    continue
                self.ch_list[str(value['chno'])] = Channel(str(value['chno']),value['name'],value['programs'][0][1],url=value['url'],logo=value['logo'],source1=self.name, source=self.source_name)
        #logger.debug(d(self.ch_list))
        return self.ch_list

DATA_URL = 'https://i.mjh.nz/SamsungTVPlus/app.json.gz'
EPG_URL = 'https://i.mjh.nz/SamsungTVPlus/all.xml.gz'  

#data = gzip.decompress(requests.get(EPG_URL).content).decode('utf-8')
#return Response(data, mimetype='application/xml')