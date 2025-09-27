import math
import os
import sys
import json
import random
from pathlib import Path

DATA_PATH = Path(__file__).with_name("bank_data.json")

x = list(map(lambda x: x**2, [2, 3, 5, 10, 11]))
print(x)

def interest(principle, annual_rate, times_compunded, time_periods):
    if principle < 0 or annual_rate < 0 or times_compunded <= 0 or time_periods < 0:
        raise ValueError("All parameters must be non-negative and times_compunded must be positive.")
    
    return principle * (1 + annual_rate / times_compunded) ** (times_compunded * time_periods)

class Client:
    def __init__(self, name, age, ssn, bankId=0):
        bankId_range = range(100000, 1000000)
        self.name = name
        self.age = age
        self.ssn = ssn
        self.balance = 0.0
        self.transactions = []

        if not bankId in bankId_range:
            self.bankId = random.randrange(100000, 999999)
        else:
            self.bankId = bankId
    
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        self.transactions.append(f"Deposited: ${amount:.2f} | Date: {os.path.getmtime(__file__)}")
    
    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds for withdrawal.")
        
        self.balance -= amount
        self.transactions.append(f"Withdrew: ${amount:.2f} | Date: {os.path.getmtime(__file__)}")
    
    def get_balance(self):
        return self.balance
    
    def get_important_info(self):
        return [self.ssn, self.bankId]

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "ssn": self.ssn,
            "balance": self.balance,
            "bankId": self.bankId,
            "transactions": self.transactions,
        }

    @staticmethod
    def from_dict(data):
        client = Client(
            name=data["name"],
            age=int(data["age"]),
            ssn=int(data["ssn"]),
            bankId=int(data["bankId"]),
        )
        client.balance = float(data.get("balance", 0.0))
        client.transactions = list(data.get("transactions", []))
        return client

class Bank:
    def __init__(self):
        self.clients = []
    
    def add_client(self, client):
        self.clients.append(client)
    
    def remove_client(self, client):
        self.clients.remove(client)
    
    def get_client_by_name(self, name):
        for c in self.clients:
            if c.name.lower() == name.lower():
                return c
        return None

    def get_client_by_id(self, bankId):
        for c in self.clients:
            if c.bankId == bankId:
                return c
        return None
    
    def load(self, path: Path = DATA_PATH):
        if not path.exists() or path.stat().st_size == 0:
            self.clients = []
            return

        try:
            with path.open("r", encoding="utf-8") as f:
                clients_data = json.load(f)
            self.clients = [Client.from_dict(cd) for cd in clients_data]
        except json.JSONDecodeError as e:
            print(f"Warning: {path.name} is invalid JSON: {e}")
            try:
                print("File contents:\n", path.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                pass
            self.clients = []
        except Exception as e:
            print(f"Unexpected error reading {path}: {e}")
            self.clients = []

    def save(self, path: Path = DATA_PATH):
        tmp = path.with_suffix(".json.tmp")
        data = [c.to_dict() for c in self.clients]
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            f.flush()
        tmp.replace(path)

bank = Bank()
bank.load()

while True:
    choice = str(input("What would you like to do?\n(1) Login (Y)\n(2) Exit (E)\n\n"))
    if choice == "E":
        break

    name, age, ssn, bId = str(input("Hello, please put your information here: [Name] [Age] [SSN] [Bank ID, 0 if you do not have one!]\n")).split()
    person = None

    if int(bId) != 0:
        person = bank.get_client_by_id(int(bId))
    else:
        person = bank.get_client_by_name(name)

    if person is None:
        person = Client(name, int(age), int(ssn), int(bId))
        bank.add_client(person)

    task = int(input("Hello there, welcome to the bank, what would you like to do today?\n(1) Depost money\n(2) Withdraw money\n(3) Show my balance\n(4) Retrieve my information\n"))
    if task == 1:
        amount = int(input(f"How much would you like to deposit [BALANCE: {person.balance}]: "))
        person.deposit(amount)
        print(f"Thank you. Your new balance is {person.balance}")
    elif task == 2:
        amount = int(input(f"How much would you like to withdraw [BALANCE: {person.balance}]: "))
        person.withdraw(amount)
        print(f"Thank you. Your new balance is {person.balance}")
    elif task == 3:
        print(f"Your current balance is: {person.balance:.2f}")
    elif task == 4:
        print(f"DISCLAIMER: DO NOT SHOW THIS TO ANYONE\n\nYour SSN: {person.ssn}\nYour Bank ID Number: {person.bankId}")

bank.save()
