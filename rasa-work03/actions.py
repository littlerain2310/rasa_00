from typing import Any, Text, Dict, List
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from rasa_sdk.events import SlotSet,Form,ReminderScheduled,ActionReverted,UserUtteranceReverted,FollowupAction,AllSlotsReset
from rasa.core.slots import Slot
import datetime
import time
from threading import Timer


class BeginForm(FormAction):
    def name(self):
        return "begin_form"
    @staticmethod
    def required_slots(tracker)-> List[Text]:
        if tracker.get_slot("contents")=="Khác":
            return ["contents"]
        else:
            return ["contents","services"]
    @staticmethod
    def contents_db() -> List[Text]:
        '''database of contents'''
        return [
            "tư vấn sản phẩm dịch vụ",
            "tư vấn việc làm",
            "khác",
        ]
    @staticmethod
    def services_db() -> List[Text]:
        '''database of services'''
        return [
            "phần mềm contact center",
            "dịch vụ telesales",
            "dịch vụ chăm sóc khách hàng",
            "dịch vụ mystery shopping",
            "dịch vụ tuyển dụng",
            "dịch vụ đào tạo",
            "dịch vụ nhập liệu",
            "dịch vụ field-work",
        ]
    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        )  ->List[Dict]:
        if tracker.get_slot("contents")=="Khác":
            dispatcher.utter_message("Vui lòng liên hệ với agent")
            return []
        else:
            return []
    def slot_mappings(self) :
        return { 
            "contents": [self.from_entity(entity="contents",not_intent="chitchat"),
                        self.from_text()
            ],
            "services": [self.from_entity(entity="services",not_intent="chitchat"),
                        self.from_text()
                        ]
        }
    def validate_contents(self,value: Text, dispatcher, tracker, domain) ->List[Text]:
        if value.lower() in self.contents_db():
            return {"contents": value}
        else:
            return {"contents": None}
    def validate_services (self,value: Text, dispatcher, tracker, domain) ->List[Text]:
        if value.lower() in self.services_db():
            return {"services": value}
        else:
            return {"services": None}

class MiddleForm(FormAction):
    def name(self):
        return "middle_form"
    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        )  ->List[Dict]:
        
        return []
    @staticmethod
    def required_slots(tracker) -> List[Text]:
        if tracker.get_slot("choices")=='Nhận tư vấn ngay':
            if tracker.get_slot("services") == 'Dịch vụ đào tạo' :
                return ["choices","trainning_package"]
            else: 
                return ["choices","demand"]
        else:
            return ["choices","docs"]
    
    def slot_mappings(self) :
        return { 
            "demand": [
                self.from_text()
            ],
            "choices": [
                self.from_entity(entity="choices",not_intent="chichat"),
                self.from_text()
            ],
            "trainning_package": [
                self.from_entity(entity="trainning_package",not_intent="chichat"),
                self.from_text()
            ],
            "docs": [
                self.from_entity(entity="docs",not_intent="chichat"),
                self.from_text()
            ]
        }

    @staticmethod
    def choices_db() -> List[Text]:
        return [
            "nhận tư vấn ngay",
            "xem tài liệu"
        ]
    
    @staticmethod
    def trainning_package_db() -> List[Text]:
        return [
            "đào tạo dịch vụ khách hàng",
            "đào tạo kỹ năng outbound",
            "đào tạo quản trị và điều hành contact center",
            "đào tạo trải nghiệm khách hàng trong thời đại số",
            "đào tạo nâng cao năng lực quản lý cấp trung"
        ]
    
    @staticmethod
    def docs_db() -> List[Text]:
        return [
            "tìm hiểu về dịch vụ",
            "xem case study",
            "báo giá"
        ]
    
    def validate_choices (self,value: Text, dispatcher, tracker, domain) ->List[Text]:
        if value.lower() in self.choices_db():
            return {"choices": value}
        else:
            return {"choices": None}

    def validate_trainning_package (self,value: Text, dispatcher, tracker, domain) ->List[Text]:
        if value.lower() in self.trainning_package_db():
            return {"trainning_package": value}
        else:
            return {"trainning_package": None}

    def validate_docs (self,value: Text, dispatcher, tracker, domain) ->List[Text]:
        if value.lower() in self.docs_db():
            return {"docs": value}
        else:
            return {"docs": None}

class EndForm(FormAction):
    def name(self) -> Text:
        return "end_form"
    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        )  ->List[Dict]:
        if tracker.get_slot("additional_support")=="không":
            dispatcher.utter_message("Dạ, vậy em xin đóng phiên chat tại đây. Cảm ơn quý khách đã liên hệ đến BHS, nếu có thêm thông tin nào cần hỗ trợ thêm, quý khách đừng ngại chat vào đây hoặc gọi đến hotline 1900 1739 để được tư vấn nhé. Chúc quý khách một ngày tuyệt vời!")
            return []
        if tracker.get_slot("call") == "chat trực tiếp với tổng đài viên":
            dispatcher.utter_message("Chuyển đến admin trực webchat")
            return []
        else:
            dispatcher.utter_message("Chuyển đến admin webchat")
            return []


    @staticmethod
    def required_slots(tracker) -> List[Text]:
        if tracker.get_slot("call") == "Chat trực tiếp với tổng đài viên":
            return["call"]
        return [
            "call",
            "name",
            "phone",
            "email",
            "bussiness",
            "connect",
            "time",
            "additional_support"
        ]
    @staticmethod
    def additional_support_db() -> List[Text]:
        return [
            "không",
            "muốn tư vấn tiếp"
        ]
    @staticmethod
    def call_db() -> List[Text]:
        return [
            "nhận tư vấn qua điện thoại từ bộ phận kinh doanh",
            "chat trực tiếp với tổng đài viên"
        ]
    def slot_mappings(self):
        return {
            "name": [
                self.from_entity(entity="name",not_intent="chitchat"),
            ],
            "phone": [
                self.from_entity(entity="phone",not_intent="chitchat"),
                self.from_text(intent="inform")
            ],
            "email": [
                self.from_entity(entity="email",not_intent="chitchat"),
            ],
            "bussiness": [
                self.from_entity(entity="bussiness",not_intent="chitchat"),
                self.from_text(intent="inform")
            ],
            "connect":[
                self.from_text()
            ],
            "call":[
                self.from_text()
            ]
            # "additional_support":[
            #     self.from_intent(intent="deny",value=False)
            # ]
        }
    def validate(self, dispatcher, tracker, domain):
        result = []
        result.append(ReminderScheduled(intent_name="EXTERNAL_reminder",
                                        trigger_date_time=datetime.datetime.now()
                                        + datetime.timedelta(seconds=30),
                                        name="first_remind",
                                        kill_on_user_message=True))
        slot_values = self.extract_other_slots(dispatcher, tracker, domain)
        value = tracker.latest_message.get("text")
        slot_to_fill = tracker.get_slot("requested_slot")
        if slot_to_fill: 
            slot_values.update(self.extract_requested_slot(dispatcher,tracker,domain))
        if slot_to_fill=="time":
            value = tracker.latest_message["entities"]

            day = value[0]['value']
            month = value[1]['value']
            year = value[2]['value']
            
            time = "{} / {} / {}".format(day,month,year)
            result.append(SlotSet("time",time))
        if slot_to_fill == "call":
            if value.lower() in self.call_db():
                result.append(SlotSet("call", value))
            else:
                result.append(SlotSet("call",None))
        if slot_to_fill == "additional_support":
            if value.lower() in self.additional_support_db():
                result.append(SlotSet("additional_support", value))
            else:
                result.append(SlotSet("additional_support",None))
        for slot, value in slot_values.items():
            result.append(SlotSet(slot, value))
        
        return result
    # def validate_call(self,value: Text, dispatcher, tracker, domain) -> List[Dict] :
    #     result = []
    #     result.append(ReminderScheduled(intent_name="EXTERNAL_second",
    #                                     trigger_date_time=datetime.datetime.now()
    #                                     + datetime.timedelta(seconds=10),
    #                                     name="name_remind",
    #                                     kill_on_user_message=True))
    #     if value.lower() in self.call_db():
    #         result.append(SlotSet("call",value))
    #     else:
    #         result.append(SlotSet("call", None))
    #     return result 
    # def validate_name(self,value: Text, dispatcher, tracker, domain) :
    #     result = []
    #     result.append(ReminderScheduled(intent_name="EXTERNAL_second",
    #                                     trigger_date_time=datetime.datetime.now()
    #                                     + datetime.timedelta(seconds=10),
    #                                     name="name_remind",
    #                                     kill_on_user_message=True))
    #     result.append(SlotSet("name",value))
    #     return result

    # def validate_phone(self,value: Text, dispatcher, tracker, domain) -> List[Text]:
    #     result = []
    #     result.append(ReminderScheduled(intent_name="EXTERNAL_reminder",
    #                                     trigger_date_time=datetime.datetime.now()
    #                                     + datetime.timedelta(seconds=10),
    #                                     name="phone_remind",
    #                                     kill_on_user_message=True))
    #     result.append(SlotSet("phone",value))
    #     return result
    

    # def validate_bussiness(self,value: Text, dispatcher, tracker, domain) -> List[Text]:
    #     result = []
    #     result.append(ReminderScheduled(intent_name="EXTERNAL_reminder",
    #                                     trigger_date_time=datetime.datetime.now()
    #                                     + datetime.timedelta(seconds=10),
    #                                     name="bussiness_remind",
    #                                     kill_on_user_message=True))
    #     result.append(SlotSet("name",value))
    #     return result

    # def validate_email(self,value: Text, dispatcher, tracker, domain) -> List[Text]:
    #     result = []
    #     result.append(ReminderScheduled(intent_name="EXTERNAL_reminder",
    #                                     trigger_date_time=datetime.datetime.now()
    #                                     + datetime.timedelta(seconds=10),
    #                                     name="email_remind",
    #                                     kill_on_user_message=True))
    #     result.append(SlotSet("email",value))
    #     return result

    # def validate_time(
    #     self,
    #     value: List,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    # ) :
    #     """Validate birthday value."""
    #     value = tracker.latest_message["entities"]

    #     day = value[0]['value']
    #     month = value[1]['value']
    #     year = value[2]['value']
        
    #     time = "{} / {} / {}".format(day,month,year)
    #     return {"time": time}
    # def validate_additional_support (self,value: Text, dispatcher, tracker, domain) ->List[Text]:
    #     if value.lower() in self.additional_support_db():
    #         return {"additional_support": value}
    #     else:
    #         return {"additional_support": None}

class ActionInactivityScheduler(Action):
    def name(self):
        return "action_inactivity_scheduler"
    def run(self, dispatcher, tracker, domain):
        
        # intent = tracker.events[-7].get("intent", {}).get("name")
        slot_to_fill = tracker.get_slot("requested_slot")
        dispatcher.utter_template('utter_ask_{}'.format(slot_to_fill),tracker)
        # if slot_to_fill == "name":
        #     dispatcher.utter_message(tracker.events[-7].get('text'))
        # if intent == 'chichat':
        #     dispatcher.utter_template('utter_ask_{}'.format(slot_to_fill),tracker)
        # else:
        #     dispatcher.utter_message(tracker.events[-6].get('text'))
        result = []
        result.append(ReminderScheduled(intent_name="EXTERNAL_second",
                                        trigger_date_time=datetime.datetime.now()
                                        + datetime.timedelta(seconds=30),
                                        name="second_remind",
                                        kill_on_user_message=True))  
        return result

class ActionInactivitySchedulerFinal(Action):
    def name(self):
        return "action_inactivity_scheduler_final"
    def run(self, dispatcher, tracker, domain):
        return [Form(None),SlotSet("requested_slot", None)]