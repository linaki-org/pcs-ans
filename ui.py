from tkinter import *
from tkinter.simpledialog import askstring
from PIL import Image, ImageTk


class UI:
    def __init__(self, game):
        self.tk = Tk()
        self.tk.title("My Pcs-Ans game")
        self.gameFrame = Frame(self.tk)
        self.gameFrame.pack()
        self.controlFrame = Frame(self.tk)
        self.controlFrame.pack()
        self.game = game
        self.game.tk = self.gameFrame
        self.game.HEIGHT = 850
        self.game.WIDTH = 1920
        self.use = Button(self.controlFrame, text="Use", command=lambda: self.act("use"))
        self.pickup = Button(self.controlFrame, text="Pick up", command=lambda: self.act("pick"))
        self.lookat = Button(self.controlFrame, text="Look at", command=lambda: self.act("look"))
        self.goto = Button(self.controlFrame, text="Go to", command=lambda: self.act("go"))
        self.open = Button(self.controlFrame, text="Open", command=lambda: self.act("open"))
        self.inventoryLabels = []
        self.images = []
        self.use.pack(side=LEFT)
        self.pickup.pack(side=LEFT)
        self.lookat.pack(side=LEFT)
        self.goto.pack(side=LEFT)
        self.open.pack(side=LEFT)
        self.commandLabel = Label(self.controlFrame, text="")
        self.commandLabel.pack()
        self.command = "go"
        self.tk.bind("<KeyPress-Right>", lambda e: self.game.addOffset(self.game.OFFSET))
        self.tk.bind("<KeyPress-Left>", lambda e: self.game.addOffset(-self.game.OFFSET))

    def act(self, action):
        self.command = action
        self.commandLabel.config(text=self.command)

    def handleObject(self, id):
        print(id)
        self.command += " " + id
        print(self.command)
        if self.game.trigger(self.command):
            self.command = "go"
        if len(self.command.split(" ")) >= 3:
            self.command = "go"
        self.commandLabel.config(text=self.command)

    def genObjectHandler(self, object):
        return lambda e: self.handleObject(object)

    def updateInventory(self):
        for label in self.inventoryLabels:
            label.destroy()
        self.inventoryLabels = []
        for object in self.game.inventory:
            print(object)
            img = Image.open("objects/" + self.game.objects[object][1][-1])
            self.images.append(ImageTk.PhotoImage(img))
            self.inventoryLabels.append(Label(self.controlFrame, image=self.images[-1]))
            self.inventoryLabels[-1].pack(side=RIGHT)
            self.inventoryLabels[-1].bind("<Button-1>", self.genObjectHandler(object))

    def mainloop(self):
        #self.game.exec("goroom house_interior")
        self.tk.bind("<Button-1>", print)
        self.tk.bind("<KeyPress-g>", lambda e: self.game.exec(askstring("PCS-ANS cheat", "Enter game command :")))
        self.tk.mainloop()


if __name__ == "__main__":
    import runnerEngine