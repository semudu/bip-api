from requests.auth import HTTPBasicAuth
from .type import *
import requests
import random
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class Api:
    def __init__(self, url, username, password):
        self.all = GroupApi(url, username, password)
        self.one = MemberApi(url, username, password)


class BaseApi:
    def __init__(self, url, username, password, address_type):
        self.url = url
        self.headers = {"Content-Type": "application/json"}
        self.auth = HTTPBasicAuth(username, password)
        self.address_type = address_type
        logging.debug("BIP initialized for username: %s, password: %s" % (username, password))

    @staticmethod
    def __get_txnid__():
        return random.randint(1000, 9999)

    def __get_receiver_json__(self, receiver):
        json_data = {
            "type": self.address_type.value
        }

        if self.address_type == AddressType.MSISDN:
            json_data["address"] = "90" + receiver[-10:]
        elif self.address_type == AddressType.HASH:
            json_data["address"] = receiver

        return json_data

    def __send_message__(self, post_json):
        return requests.post(self.url, headers=self.headers, auth=self.auth, json=post_json)

    def __get_base_json__(self, receiver):
        return {
            "txnid": str(self.__get_txnid__()),
            "receiver": self.__get_receiver_json__(receiver),
            "composition": {
                "list": []
            }
        }

    def __get_post_json__(self, message_type, receiver, args_json):
        post_json = self.__get_base_json__(receiver)
        post_json["composition"]["list"].append({
            "type": message_type.value,
            **args_json
        })

        return post_json

    def __get_buttons_json__(self, buttons_tuple):
        button_list = []
        for button in buttons_tuple:
            button_list.append({
                "type": button[2].value,
                "name": button[1],
                "payload": button[0]
            })
        return button_list

    def __get_options_json__(self, options_tuple):
        option_list = []
        for option in options_tuple:
            option_list.append({
                "optionid": option[0],
                "name": option[1]
            })
        return option_list

    def send_quickreply_message(self, receiver, postback_id, buttons_tuple):
        post_json = self.__get_post_json__(MessageType.MEDIA, receiver, {
            "tmmtype": MediaMessageType.QUICK_REPLY.value,
            "quickreplytmm": {
                "buttonlist": self.__get_buttons_json__(buttons_tuple),
                "postbackid": postback_id
            }
        })
        self.__send_message__(post_json)

    def send_poll_message(self, receiver, poll_id, title, description, image_url, image_ratio, poll_type, options_tuple,
                          button_name):
        post_json = self.__get_post_json__(MessageType.MEDIA, receiver, {
            "tmmtype": MediaMessageType.POLL.value,
            "polltmm": {
                "title": title,
                "description": description,
                "polltype": poll_type.value,
                "image": {
                    "url": image_url,
                    "ratio": image_ratio
                },
                "optionlist": self.__get_options_json__(options_tuple),
                "pollid": poll_id,
                "buttonname": button_name
            }
        })
        self.__send_message__(post_json)

    def send_custom_message(self, receiver, message_type, args_json):
        post_json = self.__get_post_json__(message_type, receiver, args_json)
        self.__send_message__(post_json)

    def send_text_message(self, receiver, message):
        post_json = self.__get_post_json__(MessageType.TEXT, receiver, {
            "message": message
        })
        self.__send_message__(post_json)

    def send_image(self, receiver, image_url, image_size, ratio):
        post_json = self.__get_post_json__(MessageType.IMAGE, receiver, {
            "message": image_url,
            "size": image_size,
            "ratio": ratio
        })
        self.__send_message__(post_json)

    def send_audio(self, receiver, audio_url, audio_size):
        post_json = self.__get_post_json__(MessageType.AUDIO, receiver, {
            "message": audio_url,
            "size": audio_size
        })
        self.__send_message__(post_json)

    def send_video(self, receiver, video_url, video_size, ratio):
        post_json = self.__get_post_json__(MessageType.VIDEO, receiver, {
            "message": video_url,
            "size": video_size,
            "ratio": ratio
        })
        self.__send_message__(post_json)

    def send_sticker(self, receiver, sticker_url, item_id):
        post_json = self.__get_post_json__(MessageType.STICKER, receiver, {
            "message": sticker_url,
            "itemid": item_id
        })
        self.__send_message__(post_json)

    def send_caps(self, receiver, caps_url, item_id, size, ratio):
        post_json = self.__get_post_json__(MessageType.CAPS, receiver, {
            "message": caps_url,
            "itemid": item_id,
            "ratio": ratio,
            "size": size
        })
        self.__send_message__(post_json)

    def send_location(self, receiver, latitude, longitude, title, description, zoom_level):
        post_json = self.__get_post_json__(MessageType.LOCATION, receiver, {
            "location": {
                "lat": latitude,
                "lon": longitude,
                "title": title,
                "desc": description,
                "zoomlevel": zoom_level
            }
        })
        self.__send_message__(post_json)

    def send_line(self, receiver):
        post_json = self.__get_post_json__(MessageType.LINE, receiver, None)
        self.__send_message__(post_json)

    # contact_json example
    #
    # {
    #     "name": "Cemal",
    #     "surname": "Önder",
    #     "phonenumbers": ["905332108323", "905XXXXXXXXX"],
    #     "addresses": [{
    #         "address": "Bahçelievler, Yenibosna, Atatürk Caddesi",
    #         "postalcode": "34197",
    #         "city": "İstanbul",
    #         "country": "Türkiye"
    #     }]
    # }
    def send_contact(self, receiver, contact_json):
        self.send_custom_message(MessageType.CONTACT, receiver, contact_json)

    def send_document(self, receiver, filename, filepath):
        post_json = self.__get_post_json__(MessageType.DOCUMENT, receiver, {
            "document": {
                "filename": filename,
                "filepath": filepath
            }
        })
        self.__send_message__(post_json)


class GroupApi(BaseApi):
    def __init__(self, url, username, password):
        super().__init__(url, username, password, AddressType.ALL_MEMBERS)

    def send_quickreply_message(self, postback_id, buttons_tuple):
        super().send_quickreply_message(None, postback_id, buttons_tuple)

    def send_poll_message(self, poll_id, title, description, image_url, image_ratio, poll_type, options_tuple,
                          button_name):
        super().send_poll_message(None, poll_id, title, description, image_url, image_ratio, poll_type, options_tuple,
                                  button_name)

    def send_custom_message(self, message_type, args_json):
        super().send_custom_message(None, message_type, args_json)

    def send_text_message(self, message):
        super().send_text_message(None, message)

    def send_image(self, image_url, image_size, ratio):
        super().send_image(None, image_url, image_size, ratio)

    def send_audio(self, audio_url, audio_size):
        super().send_audio(None, audio_url, audio_size)

    def send_video(self, video_url, video_size, ratio):
        super().send_video(None, video_url, video_size, ratio)

    def send_sticker(self, sticker_url, item_id):
        super().send_sticker(None, sticker_url, item_id)

    def send_caps(self, caps_url, item_id, size, ratio):
        super().send_caps(None, caps_url, item_id, ratio)

    def send_location(self, latitude, longitude, title, description, zoom_level):
        super().send_location(None, latitude, longitude, title, description, zoom_level)

    def send_line(self):
        super().send_line(None)

    # contact_json example
    #
    # {
    #     "name": "Cemal",
    #     "surname": "Önder",
    #     "phonenumbers": ["905332108323", "905XXXXXXXXX"],
    #     "addresses": [{
    #         "address": "Bahçelievler, Yenibosna, Atatürk Caddesi",
    #         "postalcode": "34197",
    #         "city": "İstanbul",
    #         "country": "Türkiye"
    #     }]
    # }
    def send_contact(self, contact_json):
        super().send_contact(None, contact_json)

    def send_document(self, filename, filepath):
        super().send_document(None, filename, filepath)


class MemberApi(BaseApi):
    def __init__(self, url, username, password):
        super().__init__(url, username, password, AddressType.MSISDN)