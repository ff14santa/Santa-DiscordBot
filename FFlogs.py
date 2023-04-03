import requests

class FFlogs:
    def __init__(self, FFLOG_CLIENT, FFLOG_SECRET):
        self.FFLOG_CLIENT = FFLOG_CLIENT
        self.FFLOG_SECRET = FFLOG_SECRET
        self.refresh()

    def refresh(self):
        self.refresh_token()
        self.refresh_latest_expansion()
        self.refresh_latest_savages()

    def get(self, body):
        url = "https://ko.fflogs.com/api/v2/client"

        response = requests.post(url=url, headers={'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}, json={"query": body})
        if response.status_code == 200:
            return response.json()

        else:
            self.refresh_token()
            return self.get(body)

    def refresh_token(self):
        print("refresh_token")
        response = requests.post(
            "https://ko.fflogs.com/oauth/token",
            data={"grant_type": "client_credentials"},
            auth=(self.FFLOG_CLIENT, self.FFLOG_SECRET),
        )
        try:
            self.token = response.json()["access_token"]
        except:
            self.refresh_token()

    def refresh_latest_expansion(self):
        print("refresh_latest_expansion")
        body = """
        {
            worldData {
                expansions {
                    id
                }
            }
        }
        """
        expansions = self.get(body)
        expansions = expansions['data']['worldData']['expansions']
        expansions = sorted(expansions, key=lambda d: d['id'], reverse=True)
        self.latest_expansion = expansions[0]['id']

    def refresh_latest_savages(self):
        print("refresh_latest_savages")
        body = """
            {
                worldData {
                    expansion(id: %d) {
                        zones {
                            id
                            difficulties {
                                id
                                sizes
                            }
                            encounters {
                                id
                                name
                            }
                        }
                    }
                }
            }
        """ % self.latest_expansion
        zones = self.get(body)['data']['worldData']['expansion']['zones']

        for zone in zones:
            if len([difficulty for difficulty in zone['difficulties'] if difficulty['id'] == 101 and difficulty['sizes'] == [8]]) > 0:
                self.latest_zone = zone['id']
                self.latest_encounters = {item['id']: item['name'] for item in zone['encounters']}
                break

    def get_fflogs(self, name, server):
        print(f'https://ko.fflogs.com/character/kr/{server}/{name}')
        body = """
            {
                characterData {
                    character(name: "%s", serverSlug: "%s", serverRegion: "KR") {
                        zoneRankings(zoneID: %d, difficulty: 101, metric: rdps)
                    }
                }
            }
          """ % (name, server, self.latest_zone)
        try:
            return {self.latest_encounters[item['encounter']['id']]: {'rankPercent': item['rankPercent'], 'bestSpec': item['bestSpec']} for item in self.get(body)['data']['characterData']['character']['zoneRankings']['rankings']}
        except TypeError:
            return dict()
