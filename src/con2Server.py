import xmpp
import slixmpp
import logging
from domain import load_domain

logging.basicConfig(level=logging.ERROR)
logging.getLogger('slixmpp').setLevel(logging.ERROR)

DOMAIN = load_domain()

class Con2Server(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.loggedIn = False

    async def startSession(self, event):
        self.send_presence()
        await self.get_roster()
        self.loggedIn = True
        self.disconnect()

def newUser(jid, password):
    xmppJid = xmpp.JID(jid)
    xmppAccount = xmpp.Client(xmppJid.getDomain(), debug=[])
    xmppAccount.connect()

    xmppStatus = xmpp.features.register(
        xmppAccount,
        xmppJid.getDomain(),
        { "username": xmppJid.getNode(), "password": password }
    )

    return bool(xmppStatus)

async def sendFriendRequest(xmpp_client: slixmpp.ClientXMPP):
    friendsUser = input("who would you like to send a friend request to? (username): ")
    potentialFriendsUser = f"{friendsUser}@{DOMAIN}"
    xmpp_client.send_presence_subscription(potentialFriendsUser)
    print("-> you just sent a friend request to", potentialFriendsUser)
    await xmpp_client.get_roster()

async def requestsManagement(xmpp_client: slixmpp.ClientXMPP, presence):
    print(f"received presence from {presence['from']} of type {presence['type']}")
   
    
    if presence["type"] == "subscribe":
        
        xmpp_client.send_presence(pto=presence['from'], ptype='subscribed')
        if not xmpp_client.usersContacts[presence['from']].subscription_to:
            xmpp_client.send_presence_subscription(presence['from'], ptype='subscribe')
        print(f"accepted and reciprocated subscription with {presence['from']}")
    
    elif presence['type'] == 'subscribed':
        await xmpp_client.get_roster()
        roster_item = xmpp_client.usersContacts[presence['from']]
        if not (roster_item['subscription_to'] and roster_item['subscription_from']):
            print("subscription not mutual, fixing...")
            xmpp_client.send_presence_subscription(presence['from'], ptype='subscribe')

async def changeStatus(self):
    print("\t1. available")
    print("\t2. in something but can chat")
    print("\t3. away")
    print("\t4. occupied")
    status = input("\nwhat's the number of the status you would like to change to ?: ")

    if status == "1":
        presence = "available"
    elif status == "2":
        presence = "some"
    elif status == "3":
        presence = "away"
    elif status == "4":
        presence = "ocp"
    else:
        presence = "available"

    description = input("Enter your own description: ")
    self.send_presence(pshow=presence, pstatus=description)
    await self.get_roster()

async def friendsInfo(self):
    friendsUser = input("\nEnter contact username: ")
    fullUsername = f"{friendsUser}@{DOMAIN}"

    usersContacts = self.client_roster

    found = False

    if not usersContacts:
        print("\nNo contacts found")
        return

    presenceMapping = {
        "available": "available",
        "some": "in something but can chat",
        "away": "away",
        "ocp": "occupied",
    }

    for contact in usersContacts.keys():
        
        if contact == fullUsername:

            found = True
            print(f"\nEnter full username: {contact}")

            presenceVal = "Offline"
            status = "None"
            for _, presence in usersContacts.presence(contact).items():
                presenceType = presence["show"] or "Offline"
                presenceVal = presenceMapping.get(presenceType, "Offline")

                status = presence["status"] or "None"

            print(f"status: {presenceVal}")
            print(f"description: {status}\n")

    if not found:
        print("\nYou are not friends with this user")

async def friendsList(self):
    usersContacts = self.client_roster

    if (not usersContacts):
        print("No contacts found")
        return

    for contact in usersContacts.keys():

        if (contact == self.boundjid.bare):
            continue

        print(f"\nEnter full username: [{contact}]")
        presenceVal = "offline"
        status = "none"

        for _, presence in usersContacts.presence(contact).items():
            presenceVal = presence["show"] or "offline"
            status = presence["status"] or "none"

        print(f"status: {presenceVal}")
        print(f"description: {status}")