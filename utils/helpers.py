import requests

class Location:

    def get_ip():
        try:
            response = requests.get('https://api.ipify.org?format=json')
            id_data = response.json()
            return id_data['ip']
        except Exception as e:
            print(f"Error getting IP: {e}")
        return None


    def get_location():
        try:
            ip = Location.get_ip()
            if not ip:
                return None, None
            response = requests.get("http://ip-api.com/json/{}".format(ip))
            data = response.json()
            if data['status'] == 'success':
                return data["city"]
        except Exception as e:
            print(f"Error getting location: {e}")
        return None

