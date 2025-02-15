from tkinter import *
import ui
import os
from PIL import Image, ImageTk
from time import sleep
import json
import pygame
import applets
from bvPlayer import VideoPlayer


# from colorama import Fore
class Game:
    def __init__(self):
        self.ROOMS = "rooms/"
        self.OBJECTS = "objects/"
        self.WIDTH = 1920
        self.HEIGHT = 1080
        self.OFFSET = 300
        self.MOVEZONE = 300
        self.tk = None
        self.ui = ui.UI(self)
        self.animations = {}
        self.vars = {}
        self.inventory = []
        if not self.tk:
            raise SystemError("UI must define the game frame by setting game.tk")
        self.canvas = Canvas(self.tk, height=self.HEIGHT, width=self.WIDTH)
        self.canvas.pack()
        if not os.path.exists("rooms.pcs"):
            raise FileNotFoundError("Cannot find rooms.pcs")
        elif not os.path.exists("objects.pcs"):
            raise FileNotFoundError("Cannot find objects.pcs")
        elif not os.path.exists("when.pcs"):
            raise FileNotFoundError("Cannot find when.pcs")

        print("Loading game definition files...")
        self.rooms = json.load(open("rooms.pcs"))
        self.objects = json.load(open("objects.pcs"))
        self.when = json.load(open("when.pcs"))
        print("Game definition files loaded")

        self.actualRoom = {"id": None, "name": None, "file": None}
        if not self.rooms:
            raise ValueError("Rooms.pcs is empty. If you just cloned the github, read the docs at https://pcs-ans.readthedocs.io/")
        self.goRoom("root")

    def genObjectHandler(self, id):
        return lambda e: self.ui.handleObject(id)

    def imgColorkey(self, img, colorkey=(171, 0, 171, 255), replaceBy=(0, 0, 0, 0)):
        img = img.convert("RGBA")
        for x in range(img.width):
            for y in range(img.height):
                if img.getpixel((x, y)) == colorkey:
                    img.putpixel((x, y), replaceBy)
        return img

    def goRoom(self, id, resetOffset=True):
        if id not in self.rooms:
            raise NameError("Room %s does not exists" % id)
        animations = self.animations.copy()
        for animation in animations:
            self.stopAnimation(animation)
        animations = self.animations.copy()
        for animation in animations:
            self.stopAnimation(animation)
        self.animations = {}
        file, name, objects = self.rooms[id]
        img = Image.open(self.ROOMS + file)
        factor = self.HEIGHT / img.height
        img = img.resize((int(img.width * factor), self.HEIGHT))
        photoImage = ImageTk.PhotoImage(img)
        self.canvas.delete(ALL)
        self.actualRoom["id"] = id
        self.actualRoom["name"] = name
        self.actualRoom["file"] = file
        self.actualRoom["objects"] = objects
        self.actualRoom["image"] = photoImage
        if resetOffset:
            self.actualRoom["xOffset"] = 0
            self.actualRoom["yOffset"] = 0
        self.canvas.create_image(0 - self.actualRoom["xOffset"], 0 - self.actualRoom["yOffset"], anchor=NW,
                                 image=self.actualRoom["image"])
        self.actualObjects = {}
        rightZone = self.canvas.create_rectangle(self.WIDTH - self.MOVEZONE, 0, self.WIDTH, self.HEIGHT,
                                                 fill='gray', outline="", stipple='@transparent.xbm')
        self.canvas.tag_bind(rightZone, "<Button-1>", (lambda e: self.addOffset(self.OFFSET)))
        leftZone = self.canvas.create_rectangle(0, 0, self.MOVEZONE, self.HEIGHT,
                                                fill='gray', outline="", stipple='@transparent.xbm', )
        self.canvas.tag_bind(leftZone, "<Button-1>", lambda e: self.addOffset(-self.OFFSET))
        bottomZone = self.canvas.create_rectangle(0, self.HEIGHT - self.MOVEZONE, self.WIDTH, self.HEIGHT,
                                                  fill='gray', outline="", stipple='@transparent.xbm', )
        self.canvas.tag_bind(bottomZone, "<Button-1>", lambda e: self.addOffset(0, self.OFFSET))
        topZone = self.canvas.create_rectangle(0, 0, self.WIDTH, self.MOVEZONE,
                                               fill='gray', outline="", stipple='@transparent.xbm', )
        self.canvas.tag_bind(topZone, "<Button-1>", lambda e: self.addOffset(0, -self.OFFSET))
        for object in objects:
            if object not in self.objects:
                print("Error : object does not exists")
                continue
            name, files, x, y, height, width, options = self.objects[object]
            if files[0]:
                img = Image.open(self.OBJECTS + files[0])

                img = img.resize((width, height))
                img = self.imgColorkey(img)
                photoImage = ImageTk.PhotoImage(img)
                self.actualObjects[object] = photoImage
                obId = self.canvas.create_image(x - self.actualRoom["xOffset"], y - self.actualRoom["yOffset"],
                                                image=self.actualObjects[object], anchor=NW)
                self.canvas.tag_bind(obId, "<Button-1>", self.genObjectHandler(object))
            else:
                self.actualObjects[object] = None
                obId = self.canvas.create_rectangle(x - self.actualRoom["xOffset"], y - self.actualRoom["yOffset"],
                                                    x - self.actualRoom["xOffset"] + width,
                                                    y - self.actualRoom["yOffset"] + height, fill="gray", outline="",
                                                    stipple="@transparent.xbm")
                self.canvas.tag_bind(obId, "<Button-1>", self.genObjectHandler(object))

            for option in options.split(";"):
                if option == "autoTrig":
                    if "go " + object not in self.when:
                        self.when["go %s" % object] = "setObjImg %s 1;sleep 0.5" % object
                    elif ("setObjImg %s 1" % object) not in self.when["go " + object]:
                        self.when["go " + object] = ("setObjImg %s 1;sleep 0.5;" % object) + self.when["go " + object]
                    if "use " + object not in self.when:
                        self.when["use %s" % object] = "setObjImg %s 1;sleep 0.5" % object
                    elif ("setObjImg %s 1" % object) not in self.when["go " + object]:
                        self.when["use " + object] += ("setObjImg %s 1;sleep 0.5;" % object) + self.when[
                            "use " + object]
                if "autoAnimate" in option:
                    cmd, animationId, imgList, delay = option.split(" ")
                    print(cmd, animationId, imgList, delay)
                    self.animationStep(animationId, object, [int(i) for i in imgList.split(",")], int(delay))

        self.canvas.update()

    def addOffset(self, xOffset, yOffset=0):
        print("Add offset", xOffset)
        if not ((self.actualRoom["xOffset"] + xOffset <= -1) or (
                self.actualRoom["xOffset"] + xOffset + self.WIDTH >= self.actualRoom["image"].width())):
            self.actualRoom["xOffset"] += xOffset
        if not ((self.actualRoom["yOffset"] + yOffset <= -1) or (
                self.actualRoom["yOffset"] + yOffset + self.HEIGHT >= self.actualRoom["image"].height())):
            self.actualRoom["yOffset"] += yOffset
        self.goRoom(self.actualRoom["id"], False)

    def setObjImg(self, obj, id):
        name, files, x, y, height, width, options = self.objects[obj]
        if id >= len(files):
            raise IndexError("Object images index out of range")
        img = Image.open(self.OBJECTS + files[id])

        img = img.resize((width, height))
        img = self.imgColorkey(img)
        photoImage = ImageTk.PhotoImage(img)
        self.actualObjects[obj] = photoImage
        obId = self.canvas.create_image(x - self.actualRoom["xOffset"], y - self.actualRoom["yOffset"],
                                        image=self.actualObjects[obj], anchor=NW)
        self.canvas.tag_bind(obId, "<Button-1>", self.genObjectHandler(obj))
        self.canvas.update()

    def animationStep(self, animationId, objId, imgList, delay, pos=0):
        if objId not in self.actualObjects:
            return
        if pos == len(imgList):
            pos = 0
        self.setObjImg(objId, imgList[pos])
        self.animations[animationId] = self.tk.after(delay,
                                                     lambda: self.animationStep(animationId, objId, imgList, delay,
                                                                                pos + 1))

    def stopAnimation(self, animationId):
        try:
            self.tk.after_cancel(self.animations[animationId])
            del self.animations[animationId]
        except KeyError:
            print("Animation %s is not running" % animationId)

    def mainloop(self):
        self.ui.mainloop()

    def exec(self, code):
        print(code)
        waitForElse = False
        for cmd in code.split(";"):
            args = cmd.split(" ")
            name = args[0]
            print(name)
            if waitForElse:
                if name != "else":
                    continue
                else:
                    print("Found else !!")
                    waitForElse = False
                    continue
            try:
                if name == "goroom":
                    self.goRoom(args[1])
                elif name == "setObjImg":
                    self.setObjImg(args[1], int(args[2]))
                elif name == "startAnimation":
                    self.animationStep(args[1], args[2], [int(i) for i in args[3].split(",")], args[4])
                elif name == "stopAnimation":
                    self.stopAnimation(args[1])
                elif name == "if":
                    if "=" in args[1]:
                        var, value = args[1].split("=")
                        if var not in self.vars:
                            print("Variable %s does not exists" % var)
                            waitForElse = True
                            continue
                        if self.vars[var] == value:
                            continue
                        else:
                            waitForElse = True
                    elif "inventory" in args[2]:
                        if args[1] in self.inventory:
                            continue
                        else:
                            waitForElse = True
                elif name == "setVar":
                    print("Setting var %s to %s" % (args[1], args[2]))
                    self.vars[args[1]] = args[2]
                elif name == "sleep":
                    sleep(float(args[1]))
                elif name == "else":
                    break
                elif name == "music":
                    try:
                        pygame.mixer.music.fadeout(500)
                        pygame.mixer.music.set_volume(0.35)
                        pygame.mixer.music.load("music/" + args[1])
                        pygame.mixer.music.play(-1)
                    except pygame.error:
                        print("Cannot play music : Not such file or directory %s" % args[1])
                elif name == "sound":
                    print("FOUND SOUND")
                    try:
                        sound = pygame.mixer.Sound("sound/" + args[1])
                        print(repr(sound.play()))
                    except pygame.error:
                        print("Cannot play sound : Not such file or directory %s" % args[1])
                elif name == "say":
                    try:
                        sound = pygame.mixer.Sound("dialog/" + " ".join(args[1:]) + ".wav")
                        sound.set_volume(1)
                        sound.play()
                    except FileNotFoundError:
                        print("Cannot say dialog : Dialog not found : %s" % " ".join(args[1:]))
                elif name == "pick":
                    if args[1] in self.inventory:
                        continue
                    self.inventory.append(args[1])
                    self.ui.updateInventory()
                elif name == "applet":
                    if args[1] not in applets.applets:
                        print("Applet not found : %s" % args[1])
                        continue
                    else:
                        applets.applets[args[1]](self)
                elif name == "video":
                    pygame.mixer.music.stop()
                    player = VideoPlayer.VideoPlayer(self.tk, args[1])
                    player.play()
                    while not player.player.get_pause():
                        pass
                    player.canvas.destroy()
                else:
                    print("Unknown command : %s" % cmd)
            except IndexError:
                print("Missing argument : %s" % cmd)
            except TypeError:
                print("Bad argument : %s" % cmd)

    def trigger(self, trigger):
        if trigger in self.when:
            self.exec(self.when[trigger])
            return True
        else:
            if len(trigger.split(" ")) >= 3 and "default " + trigger.split(" ")[0] in self.when:
                self.exec(self.when["default " + trigger.split(" ")[0]])

            return False

    def saveGame(self):
        return {"aroom": self.actualRoom, "vars": self.vars, "inventory": self.inventory}


pygame.init()
g = Game()
g.mainloop()