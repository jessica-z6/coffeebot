import discord
from discord.ui import View, Button, Modal, TextInput
import os

# Binary Tree Code
class Node:
    def __init__(self, value, answer="", children=[], is_special=False):
        self.answer = answer
        self.value = value
        self.children = children
        self.is_special = is_special

def parseScript(filename):
    # function that takes a list of lines, and returns the root node
    def createNode(lines):
        # if the length of lines is 1, Create an End Node
        if (len(lines) == 1):
            content = lines[0].strip('\t\n').split(',')
            return Node(content[1].strip(), answer=content[0].strip(),is_special=eval(content[2].strip()))

        # Create a list of all the children nodes
        level = lines[0].count("\t") + 1
        index = 1
        children = []
        start = 1
        while (index + 1 < len(lines)):
            index += 1
            if (lines[index].count("\t") <= level):
                children.append(lines[start:index])
                start = index
        children.append(lines[start:len(lines)])

        content = lines[0].strip('\t\n').split(',')
        if (len(content) == 1):
            # Create a Root Node
            return Node(content[0], children=[createNode(child) for child in children])
        else:
            # Create a Middle Node
            return Node(content[1].strip(), answer=content[0].strip(), children=[createNode(child) for child in children])

    file = open(filename, "r")
    content = file.readlines()
    file.close()
    return createNode(content)

# Intents specify which bucket of events you want to get access to.
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

class GuessButton(Button):
    def __init__(self, node):
        super().__init__(label=node.answer)
        self.node = node

    async def callback(self, interaction):
        await self.view.handleNode(interaction, self.node)

class GuessOptionsView(View):
    def __init__(self, node):
        super().__init__()
        self.node = node
        for child in node.children:
            self.add_item(GuessButton(child))

    async def handleNode(self, interaction, node):
        if not node.children and node.is_special:
            await interaction.response.send_message(content=f"{node.value}", view=WrongView(node))
        else:
            await interaction.response.edit_message(content=node.value, view=GuessOptionsView(node))

class WrongView(View):
    def __init__(self, node):
        super().__init__()
        self.node = node

    @discord.ui.button(label="Okay", style=discord.ButtonStyle.danger)
    async def wrong_button(self, interaction, button):
        modal = FeedbackModal(self.node)
        await interaction.response.send_modal(modal)

class FeedbackModal(Modal):
    def __init__(self, node):
        super().__init__(title='Feedback')
        self.node = node
        self.question = TextInput(label="A question to distinguish your drink.")
        self.correctAnswer = TextInput(label="What response you want for your answer?")
        self.newAnswer = TextInput(label="What is a new choice answer?")
        self.currentAnswer = TextInput(label="What is the current choice answer?")
        self.add_item(self.question)
        self.add_item(self.correctAnswer)
        self.add_item(self.newAnswer)
        self.add_item(self.currentAnswer)

    async def on_submit(self, interaction):
        newChildren = [
            Node(self.node.value, answer=self.currentAnswer.value),
            Node(self.correctAnswer.value, answer=self.newAnswer.value)
        ]
        self.node.value = self.question.value
        self.node.children = newChildren
        await interaction.response.send_message("I see. The smartest bot is ready for your next question!")

root = parseScript('script.txt')

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$coffeechat'):
        await message.channel.send(content=root.value, view=GuessOptionsView(root))

token = os.getenv("DISCORD_BOT_SECRET")
client.run(token)

