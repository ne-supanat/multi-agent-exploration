class Ticker:
    def __init__(self, canvas):
        self.maxTick = 150
        self.tick = 0
        self.tickSpeed = 300

        canvas.bind("<space>", lambda event: self.changeTickSpeed())
        canvas.bind("<Button-1>", lambda event: self.changeTickSpeed())

    def getTickSpeed(self):
        return self.tickSpeed

    def changeTickSpeed(self, event=None):
        if self.tickSpeed == 300:
            self.tickSpeed = 150
        elif self.tickSpeed == 150:
            self.tickSpeed = 50
        else:
            self.tickSpeed = 300

        print(f"current speed:{self.tickSpeed}")

    def nextTick(self):
        self.tick += 1

    def isReachMaxTick(self):
        return self.tick >= self.maxTick
