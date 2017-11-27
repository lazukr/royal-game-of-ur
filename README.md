# Royal Game of Ur

This is an ancient race game played during the time of an early civilization known as Sumer. You can read more about this game in Wikipedia [here](https://en.wikipedia.org/wiki/Royal_Game_of_Ur). 

## How to use

Please make sure to use Python 3.5+ when running this. If you wish to keep your Python environment clean, you can use the following to create a virtual environment. Below is a guide for setting up a virtual environment. If you do not wish to do so, skip directly to the Dependencies section.

### Setting up Virtual Environment

Assuming you do not have `virtualenv` installed, use whichever command that works for you:

`$ sudo apt-get install python-virtualenv`
`$ sudo easy_install virtualenv`
`$ sudo pip install virtualenv` (I recommend as I use this)

Afterwards, find a folder where you would like to put your virtual environment and run the following:

`$ virtualenv -p python3 <name>`

Replace `<name>` with whatever you find is suitable. After that, you can activate this environment by running

`$ source ./<name>/bin/activate`

You can tell you are in the environment because your command lines will be prefixed with `(<name>)`. 

To exit out of this environment, simply do enter `deactivate` into the console.

### Installing Dependencies

All the dependencies required by the game is listed in the `requirements.txt`. You can install them all with `pip` by running

`$ sudo pip install -r requirements.txt`

### Running the Game

To run the game, simply do 

`$ python3.5 ./game.py`

## Gameplay

This game involves two players trying to get all seven stones across the path before their opponent. The path that each stone takes is kind of hard to explain so I will put up an image that will explain that eventually.

### Rules
- Each turn, you roll the slot machine and add up the number you get from it. That is the amount of tiles you can choose to move one of your stone.
- You can either choose to move an existing stone or put a new one on the board.
- At any of the petal-like tile, you are protected from the enemy and you get to move again. This can be chained indefinitely as long as you keep landing the on the petal-like tiles.
- If the tile that you land on is occupied by the opponent, you can take it off the board and your opponent will have to retry the whole path for that stone.
- When coming off the board, you must get the exact amount needed to just get off.
- In any case where the previous sets of rules prevent you from making a move at all, your turn is skipped.

## TO-DO LIST
- [ ] Recreate Game class
- [ ] Add a menu
- [ ] Add multiplayer functionality
- [ ] Add an AI (unsure)


