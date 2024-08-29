# XMPPClient
A Python-based XMPP client with a graphical user interface built using Tkinter. This project allows users to sign up, log in, and manage their XMPP accounts, including sending messages, managing contacts, and more.

## Features

- **User Management**: Sign up, log in, and delete accounts.
- **Messaging**: Send and receive messages, including file transfer.
- **Contact Management**: Add, view, and manage your contacts.
- **Multi-User Chat**: Join and create chat rooms.
- **Status Management**: Set your online status and presence messages.
- **Graphical Interface**: A clean and modern GUI with customizable themes.

## Requirements

- Python 3.8+
- `slixmpp` library
- `tkinter` library (usually included with Python)
- `python-dotenv` for managing environment variables

## Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/XMPPClient.git
cd XMPPClient
```

### Set Up Environment Variables

It's important to check for installation issues as this project uses a lot of libraries that are not pre-installed on Python3.

Create a `.env` file in the root of the project to store your environment variables. For example:

```bash
"DOMAIN=your-xmpp-domain.com"
```

Make sure to replace `your-xmpp-domain.com` with the actual domain of your XMPP server.

## Usage

### Run the Application

After setting up the environment and installing the dependencies, you can run the application:

```bash
python src/main.py
```

### Functionality

- **Log In**: Use your XMPP credentials to log in.
- **Sign Up**: Create a new XMPP account directly from the client.
- **Delete Account**: Remove your account from the XMPP server.
- **Messaging**: Send text messages and files to your contacts.
- **Contact Management**: Add and view your contacts, check their status.
- **Multi-User Chat**: Join or create chat rooms and communicate with multiple users.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes and commit them with a descriptive message.
4. Push your changes to your forked repository.
5. Open a pull request to the main repository.

### Example

```bash
git checkout -b feature-awesome-feature
# Make your changes
git commit -m \"Add awesome feature\"
git push origin feature-awesome-feature
```

Then, create a pull request from your forked repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project uses the [slixmpp](https://slixmpp.readthedocs.io/) library for XMPP communication.
- Thanks to all contributors and open-source libraries that made this project possible.
