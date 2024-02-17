import discord
from discord.ui import View, Button, Modal, TextInput
import os
from keep_alive import keep_alive


# Binary Tree Code
class Node:

  def __init__(self, value, answer="", children=[]):
    self.answer = answer
    self.value = value
    self.children = children


# option1a = Node("Dog", answer="Yes")
# option1b = Node("Wolf", answer="No")

# option1 = Node("Is it a pet", answer="Yes", children=[option1a, option1b])
# option2 = Node("Lizard", answer="No")
# root = Node("Is it a mammal?", children=[option1,option2])


def parseScript(filename):
  # function that takes a list of lines, and returns the root node
  def createNode(lines):
    # if the length of lines is 1, Create an End Node
    if (len(lines) == 1):
      content = lines[0].strip('\t\n').split(',')
      return Node(content[1].strip(), answer=content[0].strip())

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
      return Node(content[0],
                  children=[createNode(child) for child in children])
    else:
      # Create a Middle Node
      return Node(content[1].strip(),
                  answer=content[0].strip(),
                  children=[createNode(child) for child in children])

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
    self.node = node
    super().__init__(label=node.answer)

  async def callback(self, interaction):
    await self.view.handleNode(interaction, self.node)


class GuessOptionsView(View):

  def __init__(self, node):
    super().__init__()
    for option in node.children:
      self.add_item(GuessButton(option))

  async def handleNode(self, interaction, node):
    # if there's no children, then it's the last node. Make the guess
    if (node.children == []):
      await interaction.response.send_message(content=f'{node.value}')
    # otherwise, ask the next question.
    else:
      await interaction.response.send_message(content=node.value,
                                              view=GuessOptionsView(node))


class WrongView(View):

  def __init__(self, node):
    super().__init__()
    self.node = node

  @discord.ui.button(label="Wrong")
  async def buttonCallback(self, interaction, button):
    await interaction.response.send_modal(FeedbackModal(self.node))


class FeedbackModal(Modal):

  def __init__(self, node):
    self.node = node
    super().__init__(title='Machine Learning')
    self.question = TextInput(label=f'A question to distinguish {node.value}')
    self.animal = TextInput(label="What kind of coffe drinker you are?")
    self.newAnswer = TextInput(label="And what is the answer to the question?")
    self.currentAnswer = TextInput(label=f'What answer gets {node.value}?')
    self.add_item(self.question)
    self.add_item(self.animal)
    self.add_item(self.newAnswer)
    self.add_item(self.currentAnswer)

  async def on_submit(self, interaction):
    newChildren = [
      Node(self.node.value, answer=self.currentAnswer.value),
      Node(self.animal.value, answer=self.newAnswer.value)
    ]
    self.node.value = self.question.value
    self.node.children = newChildren
    await interaction.response.send_message(
      f'Thanks! Algorithm is updating....{self.animal.value}')


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


# keep_alive()
token = os.getenv("DISCORD_BOT_SECRET")
client.run(token)
