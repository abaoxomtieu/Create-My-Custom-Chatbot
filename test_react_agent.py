
from src.agents.custom_chatbot.flow import custom_chatbot
config = {"configurable": {"thread_id": "2"}}

while True:
    message_input=input(">>")
    res = custom_chatbot.invoke(
        {"messages": [{"role": "user", "content": message_input}]},
        config=config
    )
    print(res.get("messages")[-1].content)