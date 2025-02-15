===========
Pcs-Ans 2.0
===========
Pcs Ans is a cool Point and click game engine that let you create cool games without programming.

Install Pcs-Ans
---------------

To install Pcs-Ans, you just have to clone `The official github repo`_
Then, install all the requirements by running ``pip3 install -r requirements.txt``

Getting Started
---------------

To create a game using Pcs-Ans, you need to define the game world through three main components:

1. **Rooms**: The different locations within the game.
2. **Objects**: Items and interactive elements in rooms.
3. **When Conditions**: The rules and interactions that control game flow.

Defining Rooms
--------------

Rooms are defined in a JSON structure where each room has:

- An internal name
- An image (located in /rooms/)
- A display name
- A list of objects present in the room

**Example (rooms.pcs):**

.. code-block:: json

    {
        "lobby": ["lobby.png", "The Lobby", ["door", "reception_desk"]],
        "kitchen": ["kitchen.png", "The Kitchen", ["fridge", "oven"]],
        "garden": ["garden.png", "The Garden", ["fountain", "bench"]]
    }
    
Images are stored in rooms/

Defining Objects
----------------

Objects are defined with:

- A name
- Associated images
- Position and size in the room

.. code-block:: json

    {
        "object id": ["Display name", ["image1.png", "image2.png"], x, y, height, width, "options"],
    }

**Example (objects.pcs):**

.. code-block:: json

    {
        "door": ["A wooden door", ["door_closed.png", "door_open.png"], 500, 200, 100, 250, "autoTrig"],
        "fridge": ["A large fridge", ["fridge.png"], 300, 400, 120, 200, ""],
        "fountain": ["A stone fountain", ["fountain.png"], 600, 250, 150, 150, ""]
    }

One object can have multiple images. By default, the displayed image is the first in the list. You can switch between images using **When Commands**.

If you create doors, you should name them with the names of the rooms they connect. E.G : kitchen_to_living is the door connecting the kitchen to the living. You should also use "autoTrig" as an option so the object automatically switch to the second image when it's clicked (door open)

Images are stored in objects/

Defining When Conditions
------------------------

When conditions define interactions in the game, such as moving between rooms, picking up objects, or triggering animations.

**Example (when.pcs):**

.. code-block:: json

    {
        "go door": "goroom kitchen",
        "go kitchen_to_garden": "goroom garden",
        "open door": "if has_key=yes; setObjImg door 1; say door_is_open; else; say It's locked",
        "pick fridge_key": "pick fridge_key; say You picked up a small key",
        "use fridge_key fridge": "if fridge_locked=yes; setObjImg fridge 1; say You unlocked the fridge"
    }

**When trigger syntax**
The trigger is what defines when to start the actions. Triggers compose of an action followed by the object ID.

**When command syntax**
There are a lot of commands that allow you to define different interactions. Cmds are separated by ; :

- ``goroom (room)`` : change room and go to (room)
- ``pick (object)`` : add (object) to the inventory
- ``setObjImg (object) (index)`` : change the image displayed as (object) to change it to the (index) image defined in the object.pcs file
- ``say (dialog)`` : play the (dialog).wav file in the dialog folder
- ``setVar (var) (value)`` : set (var) to (value)
- ``if (var)=(value);[a];else;[b]`` : execute [a] is (var)=(value), execute [b] else.

