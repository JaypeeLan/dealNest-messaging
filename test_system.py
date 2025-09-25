#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_api():
    print(" Testing DealNest Messaging API...")
    
    try:
        # Test 1: Create message
        print("\n Creating test message...")
        response = requests.post(f"{BASE_URL}/messages/", json={
            "sender_id": 1,
            "recipient_id": 2,
            "body": "Hello Bob! This is a test message from Alice."
        })
        
        if response.status_code == 201:
            data = response.json()
            print(f" Message created! ID: {data['message']['id']}")
            print(f" Notification scheduled for: {data['notification_scheduled_for']}")
            message_id = data['message']['id']
        else:
            print(f" Failed: {response.text}")
            return
        
        # Test 2: List messages
        print("\n Listing all messages...")
        response = requests.get(f"{BASE_URL}/messages/list/")
        if response.status_code == 200:
            messages = response.json()
            print(f" Found {len(messages)} messages")
            for msg in messages:
                status = " Read" if msg['is_read'] else " Unread"
                print(f"   ID {msg['id']}: {msg['sender_username']} → {msg['recipient_username']} ({status})")
        
        # Test 3: Mark as read (optional)
        print(f"\n Want to mark message {message_id} as read? (y/n)")
        choice = input().lower()
        if choice == 'y':
            response = requests.post(f"{BASE_URL}/messages/mark-read/", json={
                "message_id": message_id
            })
            if response.status_code == 200:
                data = response.json()
                print(f" Message marked as read!")
                print(f" Notification cancelled: {data['notification_cancelled']}")
            else:
                print(f" Failed: {response.text}")
        
        print("\n Test completed!")
        print(" Check your terminal running the Django server to see email notifications!")
        
    except requests.exceptions.ConnectionError:
        print(" Cannot connect to Django server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    test_api()
