from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog

import pyperclip
from cryptography.fernet import Fernet, InvalidToken


KEY_FILE = Path.home() / ".my_encryption_app_key"


def load_or_create_key():
    """Load the saved Fernet key, or create and save one on first run."""
    if KEY_FILE.exists():
        key = KEY_FILE.read_bytes()
        # Validate that the saved file contains a usable Fernet key.
        Fernet(key)
        return key

    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)

    # Restrict file access on Unix-like systems.
    try:
        KEY_FILE.chmod(0o600)
    except OSError:
        pass

    return key


def encrypt_message(message, cipher_suite):
    return cipher_suite.encrypt(message.encode("utf-8")).decode("ascii")


def decrypt_message(encrypted_message, cipher_suite):
    return cipher_suite.decrypt(encrypted_message.encode("ascii")).decode("utf-8")


def main():
    root = tk.Tk()
    root.withdraw()  # Hide the otherwise empty Tkinter window.

    try:
        cipher_suite = Fernet(load_or_create_key())
    except (OSError, ValueError) as error:
        messagebox.showerror("Key error", f"Could not load or create the key:\n{error}")
        root.destroy()
        return

    while True:
        task = simpledialog.askstring(
            "Task",
            "Do you want to encrypt or decrypt? (type 'encrypt' or 'decrypt')",
            parent=root,
        )

        if task is None:
            break

        task = task.strip().lower()

        if task not in {"encrypt", "decrypt"}:
            messagebox.showinfo("Finished", "Choose encrypt or decrypt to continue.")
            continue

        message = simpledialog.askstring(
            "Message",
            "Enter the secret message:",
            parent=root,
        )

        if message is None:
            continue

        try:
            if task == "encrypt":
                result = encrypt_message(message, cipher_suite)
                messagebox.showinfo("Ciphertext", result, parent=root)

                if messagebox.askyesno(
                    "Copy?",
                    "Do you want to copy the ciphertext to the clipboard?",
                    parent=root,
                ):
                    pyperclip.copy(result)
                    messagebox.showinfo(
                        "Success", "Ciphertext copied to clipboard!", parent=root
                    )
            else:
                result = decrypt_message(message.strip(), cipher_suite)
                messagebox.showinfo("Plaintext", result, parent=root)

        except InvalidToken:
            messagebox.showerror(
                "Decryption failed",
                "This ciphertext is invalid or was encrypted with a different key.",
                parent=root,
            )
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=root)

    root.destroy()


if __name__ == "__main__":
    main()
