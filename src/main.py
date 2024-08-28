import asyncio
import logging
import tkinter as tk
from tkinter import messagebox
import slixmpp
from slixmpp.xmlstream.stanzabase import ET
from slixmpp.exceptions import IqError, IqTimeout
from con2Server import newUser, sendFriendRequest, changeStatus, friendsInfo, friendsList
from aioconsole import ainput
from domain import load_domain, handle_failed_auth, register_plugins, register_event_handlers

logging.basicConfig(level=logging.ERROR)
logging.getLogger('slixmpp').setLevel(logging.ERROR)

DOMAIN = load_domain()

class AccountDeleter(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid=jid, password=password)
        self.user_to_delete = jid
        self.add_event_handler("session_start", self.session_start)

    async def session_start(self, event):
        self.send_presence()
        await self.get_roster()
        await self.remove_account()
        self.disconnect()

    async def remove_account(self):
        response = self.Iq()
        response["from"] = self.boundjid.user
        response["type"] = "set"
        fragment = ET.fromstring("<query xmlns='jabber:iq:register'><remove/></query>")
        response.append(fragment)
        await response.send()
        deleted_user = self.boundjid.jid.split("/")[0]
        print(f"\nThe account [{deleted_user}] has been deleted\n")

class XMPPClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid=jid, password=password)
        self.receiver_jid = ""
        self.user_jid = jid
        self.is_logged_in = False
        self.current_group = ""
        register_event_handlers(self)
        register_plugins(self)
        self.add_event_handler("presence", self.handle_friend_request)
        self.add_event_handler("session_start", self.start_session)
        self.add_event_handler("message", self.handle_message)
        self.add_event_handler("failed_auth", handle_failed_auth)
        
    async def start_session(self, event):
        self.send_presence(pshow="chat", pstatus="You are now connected to the chat")
        self.is_logged_in = True
        await self.get_roster()
        await self.user_actions()

    async def send_message_to_user(self):
        username = input("Recipient username: ")
        recipient_jid = f"{username}@{DOMAIN}"
        self.receiver_jid = recipient_jid
        print(f"\nChatting with {recipient_jid}.")

        while True:
            message = await ainput("\nType your message: ")
            if message == "exit":
                self.user_jid = ""
                break
            else:
                print(f"{self.user_jid.split('@')[0]}: {message}")
                self.send_message(mto=recipient_jid, mbody=message, mtype="chat")
                
    async def join_chat_group(self, group_name):
        full_group_name = f"{group_name}@conference.{DOMAIN}"
        self.current_group = full_group_name
        await self.plugin["xep_0045"].join_muc(room=full_group_name, nick=self.boundjid.user)
        print(f"\nChatting in {full_group_name}.\n")

        while True:
            message = await ainput("Type your message: ")
            if message == "exit":
                self.plugin["xep_0045"].leave_muc(room=full_group_name, nick=self.boundjid.user)
                self.current_group = ""
                break
            else:
                print(f"{self.user_jid.split('@')[0]}: {message}")
                self.send_message(mto=full_group_name, mbody=message, mtype="groupchat")
    
    async def send_group_message(self):
        group_name = input("\nGroup name: ")
        await self.join_chat_group(group_name)
    
    async def handle_message(self, message):
        sender = message["mucnick"]
        if sender != self.boundjid.user:
            print(f"❑ {sender} in {message['from']}: {message['body']}\n")
    
    async def handle_friend_request(self, presence):
        if presence["type"] == "subscribe":
            self.send_presence_subscription(pto=presence["from"], ptype="subscribed")
            await self.get_roster()
            print(f"\n{presence['from']} is now your friend!\n")

    async def list_all_users(self):
        iq = self.Iq()
        iq['type'] = 'get'
        iq['to'] = DOMAIN
        iq['id'] = 'disco1'
        iq['disco_items']['node'] = ''

        try:
            response = await iq.send()
            print("\nList of items on the server:")
            for item in response['disco_items']['items']:
                print(f" - JID: {item['jid']}, Name: {item.get('name', 'N/A')}")
        except IqError as e:
            print(f"Error: {e.iq['error']['condition']}")
        except IqTimeout:
            print("Error: Request timed out")


    async def create_chat_group(self, group_name):
        try:
            full_group_name = f"{group_name}@conference.{DOMAIN}"
            def on_group_join(event):
                form = self.plugin["xep_0004"].make_form(ftype='submit', title="Configuration Form")
                form.add_field(var="muc#roomconfig_roomname", value=group_name)
                form.add_field(var="muc#roomconfig_persistentroom", value=True)
                form.add_field(var="muc#roomconfig_publicroom", value=True)
                form.add_field(var="muc#roomconfig_roomdesc", value="This is a room for chatting.")
                asyncio.create_task(self.plugin["xep_0045"].set_room_config(full_group_name, form))
                print(f"The room [{group_name}] is ready to use")

            self.add_event_handler("muc::%s::got_online" % full_group_name, on_group_join)
            await self.plugin["xep_0045"].join_muc(full_group_name, self.boundjid.user)

        except Exception as e:
            print(f"\nError: group could not be created: {str(e)}")
    
    async def user_actions(self):
        while self.is_logged_in:
            print("\nYou have this options available:")
            print("1. View contacts")
            print("2. View contact info")
            print("3. Add a contact")
            print("4. Send a message")
            print("5. Send a group message")
            print("6. Create a group")
            print("7. View all users")
            print("8. Update status")
            print("9. Exit")
            option = input("\n• Choose an option: ")
            
            if option == "1":
                await friendsList(self)
            elif option == "2":
                await friendsInfo(self)
            elif option == "3":
                await sendFriendRequest(self)
            elif option == "4":
                await self.send_message_to_user()
            elif option == "5":
                await self.send_group_message()
            elif option == "6":
                group_name = input("Group name: ")
                await self.create_chat_group(group_name)
            elif option == "7":
                await self.list_all_users()
            elif option == "8":
                await changeStatus(self)
            elif option == "9":
                print("\nGoodbye, have a nice day!")
                self.disconnect()
                self.is_logged_in = False
            else:
                print("Error: Invalid option")

class UserDialog(tk.Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.result = None

        tk.Label(self, text=message).pack(pady=10)

        # Entry fields with placeholders
        self.username_entry = tk.Entry(self)
        self.username_entry.insert(0, "user")  # Placeholder for username
        self.username_entry.bind("<FocusIn>", self.clear_placeholder)
        self.username_entry.bind("<FocusOut>", self.add_placeholder)
        self.username_entry.pack(pady=5)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.insert(0, "password")  # Placeholder for password
        self.password_entry.bind("<FocusIn>", self.clear_placeholder)
        self.password_entry.bind("<FocusOut>", self.add_placeholder)
        self.password_entry.pack(pady=5)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        tk.Button(self.button_frame, text="Ok", command=self.submit).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.username_entry.focus_set()
        self.wait_window(self)

    def clear_placeholder(self, event):
        if event.widget == self.username_entry and self.username_entry.get() == "user":
            self.username_entry.delete(0, tk.END)
        elif event.widget == self.password_entry and self.password_entry.get() == "password":
            self.password_entry.delete(0, tk.END)
            self.password_entry.config(show="*")

    def add_placeholder(self, event):
        if event.widget == self.username_entry and not self.username_entry.get():
            self.username_entry.insert(0, "user")
        elif event.widget == self.password_entry and not self.password_entry.get():
            self.password_entry.insert(0, "password")
            self.password_entry.config(show="")

    def submit(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "user":
            username = ""
        if password == "password":
            password = ""
        self.result = (username, password)
        self.destroy()

class ChatClientUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XMPP Chat")
        self.root.geometry("500x300")

        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True)

        self.welcome_label = tk.Label(self.frame, text="Welcome to the XMPP chat")
        self.welcome_label.pack(pady=10)

        self.instructions_label = tk.Label(self.frame, text="Choose an option")
        self.instructions_label.pack(pady=5)

        self.login_btn = tk.Button(self.frame, text="Log In", command=self.login)
        self.login_btn.pack(pady=5)

        self.signup_btn = tk.Button(self.frame, text="Sign Up", command=self.signup)
        self.signup_btn.pack(pady=5)

        self.deleteAccount_btn = tk.Button(self.frame, text="Delete Existing Account", command=self.delete_account)
        self.deleteAccount_btn.pack(pady=5)

        self.exit_btn = tk.Button(self.frame, text="Exit", command=self.root.destroy)
        self.exit_btn.pack(pady=5)

    def login(self):
        dialog = UserDialog(self.root, "Log In", "Enter your username and password:\nThe username has to be all the info before the @")
        if dialog.result:
            username, password = dialog.result
            if username and password:
                jid = f"{username}@{DOMAIN}"
                xmpp_client = XMPPClient(jid, password)
                xmpp_client.connect(disable_starttls=True, use_ssl=False)
                xmpp_client.process(forever=False)

    def signup(self):
        dialog = UserDialog(self.root, "Sign Up", "Enter your username and password:\nThe username has to be all the info before the @")
        if dialog.result:
            username, password = dialog.result
            if username and password:
                jid = f"{username}@{DOMAIN}"
                newUser(jid, password)
                messagebox.showinfo("Sign Up", f"Account created: [{jid}]")

    def delete_account(self):
        dialog = UserDialog(self.root, "Delete Account", "Enter your username and password:")
        if dialog.result:
            username, password = dialog.result
            if username and password:
                jid = f"{username}@{DOMAIN}"
                xmpp_delete = AccountDeleter(jid, password)
                xmpp_delete.connect(disable_starttls=True, use_ssl=False)
                xmpp_delete.process(forever=False)
                self.root.after(500, lambda: self.check_deletion_status(xmpp_delete))

    def check_deletion_status(self, xmpp_delete):
        if not xmpp_delete.is_connected():
            messagebox.showinfo("Delete Account", f"The account [{xmpp_delete.boundjid.bare}] has been deleted")
        else:
            self.root.after(500, lambda: self.check_deletion_status(xmpp_delete))

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientUI(root)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    root.mainloop()
