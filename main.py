import time
from datetime import datetime
import random
import requests
from configparser import ConfigParser
import os
import http.client, urllib
import json

    def __init__(self):
        self.config = ConfigParser()
        try:
            self.config_path = os.getcwd() + r'\config.ini'
            self.config.read(self.config_path, encoding='utf-8')
        except:
            print('读取配置文件出错，请检查文件格式')

        self.token = ''
        week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        self.data = {
            'riqi': {
                'value': f'{datetime.now().strftime("%Y-%m-%d")} {week_list[datetime.now().weekday()]}',
                
            }
        }
        self.text_data = {}
        self.zhishi_data = {}

        self.T_key = self.config.get('api', 'T_key')
        self.name = self.config.get('api', 'name')
    
    def get_color(self):
        # 获取随机颜色
        get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
        color_list = get_colors(100)
        return random.choice(color_list)

    def get_token(self):
        appid = self.config.get('api','appid')
        AppSecret = self.config.get('api','AppSecret')
        url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={AppSecret}'
        resp = requests.get(url)
        self.token = resp.json()['access_token']

    def new_info(self):
        for dic in self.data.values():
            dic['color'] = self.get_color()
        for dic in self.text_data.values():
            dic['color'] = self.get_color()
        for dic in self.zhishi_data.values():
            dic['color'] = self.get_color()

        url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={self.token}'
        try:
            opendids = eval(self.config.get('api', 'openid'))
        except:
            print('opendid 格式错误，请检查')
        for i in opendids:
            try:
                template_ids = eval(self.config.get('api', 'template_id'))
            except:
                print('template_id 格式错误，请检查')
            for key, value in template_ids.items():
                if key == '天气':
                    data = {
                        'touser': i,
                        'template_id': value,
                        'url': '',
                        'data': self.data
                    }
                elif key == '仙女':
                    data = {
                        'touser': i,
                        'template_id': value,
                        'url': '',
                        'data': self.text_data
                    }
                else:
                    data = {
                        'touser': i,
                        'template_id': value,
                        'url': '',
                        'data': self.zhishi_data
                    }

                resp = requests.post(url, json=data)
                if resp.json()['errmsg'] == 'ok':
                    print('推送成功！')

                else:
                    print('推送失败')
                    print('错误码：' + str(resp.json()['errcode']))

    def get_weather(self):
        weather_url = 'http://api.tianapi.com/tianqi/index'
        city = self.config.get('api', 'city')
        params = {
            'key': self.T_key,
            'city': city,
        }
        resp = requests.get(weather_url, params=params)
        if resp.json().get('code', '') == 200:
            data = resp.json()['newslist'][0]
            weather_info = {
                'weizhi': {
                    'value': data['area'],
                    
                },
                'tianqi': {
                    'value': data['weather'],
                    
                },
                'high': {
                    'value': data['highest'],
                    
                },
                'low': {
                    'value': data['lowest'],
                    
                },
                'wind': {
                    'value': data['wind']
                },
                'shidu': {
                    'value': data['humidity']
                }
            }
            self.data.update(weather_info)

    def countdown(self):
        # 纪念日
        love_day = self.config.get('api', 'love_day')
        lianai_time = datetime.strptime(love_day, "%Y-%m-%d")
        lianai_c = datetime.today() - lianai_time
        self.data['lianai'] = {
            'value': lianai_c.days + 1,
        }
        if (lianai_c.days + 1) % 365 == 0:
            self.data['beizhu'] = {
                'value': f'今天是恋爱纪念日哦 QAQ',
            }
        else:
            self.data['beizhu'] = {
                'value': f'想{self.name}的每一天 QAQ',
            }

    def get_birthday(self):
        birthdayd = eval(self.config.get('api', 'birthday'))
        year = datetime.now().year
        if '阳历' in birthdayd:
            birthday = birthdayd['阳历']
            url = 'http://api.tianapi.com/lunar/index?key={}&date={}-{}'
        else:
            birthday = birthdayd['阴历']
            url = 'http://api.tianapi.com/lunar/index?key={}&type=1&date={}-{}'
        resp = requests.get(url.format(self.T_key, year, birthday))
        gregoriandate = resp.json()['newslist'][0]['gregoriandate']
        if datetime.strptime(str(gregoriandate), "%Y-%m-%d") < datetime.now():
            resp = requests.get(url.format(self.T_key, year + 1, birthday))
            gregoriandate = resp.json()['newslist'][0]['gregoriandate']
        day = datetime.strptime(str(gregoriandate), "%Y-%m-%d") - datetime.now()
        day = day.days
        self.data['birthday'] = dict(value=day)

    def yunshi(self):
        url = f'http://api.tianapi.com/star/index?key={self.T_key}&astro=处女座'
        resp = requests.get(url)
        content = resp.json()['newslist'][-1]['content']
        self.text_data['yunshi'] = {
            'value': content,
            
        }

    def get_zao(self):
        url = f'http://api.tianapi.com/zaoan/index?key={self.T_key}'
        resp = requests.get(url)
        if resp.json()['msg'] == 'success':
            msg = resp.json()['newslist'][0]['content']
            self.data['zaoan'] = {
                'value': msg,
                
            }
        else:
            self.data['zaoan'] = {
                'value': '又是活力满满的一天呢！',
                
            }

    def get_cai(self):
        url = f'http://api.tianapi.com/caihongpi/index?key={self.T_key}'
        resp = requests.get(url)
        if resp.json()['msg'] == 'success':
            msg = resp.json()['newslist'][0]['content']
            self.zhishi_data['caihongpi'] = {
                'value': msg,
                
            }
        else:
            self.zhishi_data['caihongpi'] = {
                'value': '世上最美丽的小仙女，你好啊！',
                
            }

    def jingqi(self):
        # 这是计算经期
        up_c = self.config.get('api', 'jingqi')
        c_date = datetime.strptime(up_c, '%Y-%m-%d') - datetime.now()
        c_date = 28 - abs(c_date.days)
        if c_date == 0:
            up_c = datetime.now().strftime('%Y-%m-%d')
            self.config.set('api', 'jingqi', str(up_c))
            self.config.write(open(self.config_path, 'w', encoding='utf-8'))
            self.data['jingqi'] = {
                'value': f'今天是月经期第{abs(c_date) + 1}天，可能会很疼，注意休息，抱抱{self.name}',
                
            }
        elif (28 - c_date) < 7:
            self.data['jingqi'] = {
                'value': f'今天是月经期第{abs(28 - c_date) + 1}天',
                
            }
        else:
            self.data['jingqi'] = {
                'value': f'距离姨妈到访还有{abs(c_date)}天',
                
            }

    def qinghua(self):
        url = f'http://api.tianapi.com/saylove/index?key={self.T_key}'
        resp = requests.get(url)
        if resp.json()['msg'] == 'success':
            msg = resp.json()['newslist'][0]['content']
            self.text_data['qinghua'] = {
                'value': msg,
            }
        else:
            self.text_data['qinghua'] = {
                'value': f'最淳朴的话，{self.name}，我爱你！',
            }

    def music(self):
        url = f'http://api.tianapi.com/hotreview/index?key={self.T_key}'
        resp = requests.get(url)
        if resp.json()['msg'] == 'success':
            msg = resp.json()['newslist'][0]['content']
            self.text_data['music'] = {
                'value': msg,
            }
        else:
            self.text_data['music'] = {
                'value': f'生命最真挚的意义就是守护我家{self.name}~',
            }

    def shiju(self):
        url = f'http://api.tianapi.com/verse/index?key={self.T_key}'
        resp = requests.get(url)
        if resp.json()['msg'] == 'success':
            msg = resp.json()['newslist'][0]['content']
            author = resp.json()['newslist'][0]['author']
            source = resp.json()['newslist'][0]['source']
            self.zhishi_data['shiju'] = dict(value=msg)
            self.zhishi_data['author'] = dict(value=f'{source}-{author}')
        else:
            self.zhishi_data['shiju'] = dict(value='愿得一心人，白头不相离。')
            self.zhishi_data['author'] = dict(value=f'白头吟-卓文君')

    def english(self):
        url = f'http://api.tianapi.com/ensentence/index?key={self.T_key}'
        resp = requests.get(url)
        if resp.json()['msg'] == 'success':
            en = resp.json()['newslist'][0]['en']
            zh = resp.json()['newslist'][0]['zh']
            self.zhishi_data['en'] = dict(value=en)
            self.zhishi_data['zh'] = dict(value=zh)
        else:
            self.zhishi_data['en'] = dict(value='When thoughts come to my heart, I want to hug you across the square screen.')
            self.zhishi_data['zh'] = dict(value=f'思念涌上心头时，想要越过方寸的屏幕拥抱你。')

    def shun(self):
        url = f'http://api.tianapi.com/skl/index?key={self.T_key}'
        resp = requests.get(url)
        if resp.json()['msg'] == 'success':
            msg = resp.json()['newslist'][0]['content']
            self.zhishi_data['shun'] = dict(value=msg)
        else:
            self.zhishi_data['shun'] = dict(
                value='人美话不多，美里没话说。')

    def run(self):
        try:
            self.get_weather()
            self.countdown()
            self.get_birthday()
            self.yunshi()
            self.jingqi()
            self.get_zao()
            self.get_cai()
            self.qinghua()
            self.music()
            self.shiju()
            self.english()
            self.shun()

            self.get_token()
            self.new_info()
        except Exception as e:
            print(e)
            print('5s后自动关闭')
            time.sleep(5)

if __name__ == '__main__':
    w = Weather()
    w.run()
