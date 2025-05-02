import os
import pickle
from datetime import datetime
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.scrollview import ScrollView

# Database for user details
user_db = {}

# Path for saving the database file
APP_PATH = os.getcwd()
DB_FILE = os.path.join(APP_PATH, 'user_db.pkl')


class FingerprintApp(App):

    def build(self):
        self.load_user_db()

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.title_label = Label(text="Fingerprint Authentication System", size_hint=(1, 0.1))
        self.layout.add_widget(self.title_label)

        self.register_button = Button(text="Register User", size_hint=(1, 0.1))
        self.register_button.bind(on_press=self.register_user)
        self.layout.add_widget(self.register_button)

        self.verify_button = Button(text="Verify Fingerprint", size_hint=(1, 0.1))
        self.verify_button.bind(on_press=self.verify_fingerprint)
        self.layout.add_widget(self.verify_button)

        return self.layout

    def load_user_db(self):
        global user_db
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'rb') as f:
                user_db = pickle.load(f)

    def save_user_db(self):
        with open(DB_FILE, 'wb') as f:
            pickle.dump(user_db, f)

    def save_user_details(self, name, phone, reg_no, photo_path, fingerprint_image_path):
        if reg_no in user_db:
            print("Fingerprint already registered!")
            return False
        user_db[reg_no] = {
            'name': name,
            'phone': phone,
            'photo': photo_path,
            'fingerprint_image': fingerprint_image_path,
            'verification_log': [],
            'registration_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        print("User details saved successfully.")
        self.save_user_db()
        return True

    def check_fingerprint(self, fingerprint_image_path, reg_no):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if reg_no not in user_db:
            self.send_alert_to_admin("Unknown User", reg_no, timestamp)
            return False

        user = user_db[reg_no]

        if fingerprint_image_path == user['fingerprint_image']:
            # Log the verification
            user['verification_log'].append(timestamp)
            self.save_user_db()

            # ✅ Show success popup with user info
            message = f"REGISTERED USER VERIFIED\nName: {user['name']}\nReg No: {reg_no}\nTime: {timestamp}"
            self.show_popup_message("Access Granted", message)
            return True
        else:
            self.send_alert_to_admin(user['name'], reg_no, timestamp)
            return False

    def send_alert_to_admin(self, name, reg_no, time):
        message = f"ALERT: Unregistered fingerprint attempted!\nName: {name}\nRegistration Number: {reg_no}\nTime: {time}"
        print("ALERT SENT TO ADMIN:")
        print(message)

        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message, size_hint=(1, None), height=100))
        close_button = Button(text="Close", size_hint=(1, None), height=50)
        close_button.bind(on_press=self.close_alert_popup)
        popup_layout.add_widget(close_button)

        self.popup = Popup(title="Admin Alert", content=popup_layout, size_hint=(0.8, 0.4), auto_dismiss=True)
        self.popup.open()

    def close_alert_popup(self, instance):
        if hasattr(self, 'popup') and self.popup:
            self.popup.dismiss()

    def open_filechooser(self, action, callback):
        def load_selected_image(instance):
            selected = filechooser.selection
            if selected:
                self.selected_image_path = selected[0]
                print(f"Image selected from file system: {self.selected_image_path}")
                callback()

        filechooser = FileChooserIconView()
        chooser_layout = BoxLayout(orientation='vertical', spacing=10)
        chooser_layout.add_widget(filechooser)

        select_button = Button(text="Select Image", size_hint=(1, 0.2))
        select_button.bind(on_press=load_selected_image)
        chooser_layout.add_widget(select_button)

        self.filechooser_popup = Popup(title=action, content=chooser_layout, size_hint=(0.9, 0.9))
        self.filechooser_popup.open()

    def register_user(self, instance):
        self.popup_register = BoxLayout(orientation='vertical', spacing=10)

        self.name_input = TextInput(hint_text="Enter your name", size_hint=(1, None), height=40)
        self.phone_input = TextInput(hint_text="Enter your phone number", size_hint=(1, None), height=40)
        self.reg_no_input = TextInput(hint_text="Enter your registration number", size_hint=(1, None), height=40)

        self.popup_register.add_widget(self.name_input)
        self.popup_register.add_widget(self.phone_input)
        self.popup_register.add_widget(self.reg_no_input)

        submit_button = Button(text="Continue", size_hint=(1, None), height=50)
        submit_button.bind(on_press=lambda x: self.capture_and_register())
        self.popup_register.add_widget(submit_button)

        self.popup = Popup(title="Register User", content=self.popup_register, size_hint=(0.8, 0.7))
        self.popup.open()

    def capture_and_register(self):
        name = self.name_input.text
        phone = self.phone_input.text
        reg_no = self.reg_no_input.text

        if reg_no in user_db:
            self.show_popup_message("Error", "This registration number already exists.")
            return

        self.popup.dismiss()

        def after_photo():
            fingerprint_image_path = self.selected_image_path
            if self.save_user_details(name, phone, reg_no, self.selected_image_path, fingerprint_image_path):
                self.show_popup_message("Success", f"User {name} registered successfully.")

        self.open_filechooser("Select Photo (used as fingerprint for demo)", after_photo)

    def verify_fingerprint(self, instance):
        self.popup_verify = BoxLayout(orientation='vertical', spacing=10)

        self.reg_no_verify_input = TextInput(hint_text="Enter registration number", size_hint=(1, None), height=40)
        self.popup_verify.add_widget(self.reg_no_verify_input)

        verify_btn = Button(text="Select Fingerprint and Verify", size_hint=(1, None), height=50)
        verify_btn.bind(on_press=self.perform_fingerprint_verification)
        self.popup_verify.add_widget(verify_btn)

        self.popup = Popup(title="Verify Fingerprint", content=self.popup_verify, size_hint=(0.8, 0.6))
        self.popup.open()

    def perform_fingerprint_verification(self, instance):
        reg_no = self.reg_no_verify_input.text

        def after_fingerprint_select():
            fingerprint_image_path = self.selected_image_path
            if self.check_fingerprint(fingerprint_image_path, reg_no):
                self.show_popup_message("Access Granted", "Fingerprint verified successfully!")
            else:
                self.show_popup_message("Access Denied", "Fingerprint verification failed.")

        self.open_filechooser("Select Fingerprint for Verification", after_fingerprint_select)

    def show_popup_message(self, title, message):
        popup_message = BoxLayout(orientation='vertical', padding=10)

        scrollview = ScrollView(size_hint=(1, 1))
        message_label = Label(
            text=message,
            size_hint_y=None,
            halign='left',
            valign='top',
            text_size=(self.root.width * 0.7, None)
        )
        message_label.bind(texture_size=lambda instance, value: setattr(message_label, 'height', value[1]))
        scrollview.add_widget(message_label)

        close_button = Button(text="Close", size_hint=(1, None), height=50)
        close_button.bind(on_press=lambda x: self.popup.dismiss())

        popup_message.add_widget(scrollview)
        popup_message.add_widget(close_button)

        self.popup = Popup(title=title, content=popup_message, size_hint=(0.8, 0.5))
        self.popup.open()


if __name__ == '__main__':
    FingerprintApp().run()
